import Foundation
import Speech
import AVFoundation

/// Servicio de reconocimiento de voz (español)
@MainActor
class SpeechService: ObservableObject {
    @Published var isRecording = false
    @Published var transcript = ""
    @Published var isAuthorized = false

    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "es-ES"))
    private let audioEngine = AVAudioEngine()
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?

    var onFinalTranscript: ((String) -> Void)?

    /// Pedir permiso
    func requestAuthorization() async {
        let status = await SFSpeechRecognizer.requestAuthorization()
        isAuthorized = (status == .authorized)

        // También pedir permiso de micrófono
        await withCheckedContinuation { cont in
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                cont.resume()
            }
        }
    }

    /// Empezar a grabar
    func startRecording() throws {
        guard let recognizer = recognizer, recognizer.isAvailable else {
            throw SpeechError.recognizerUnavailable
        }

        // Cancelar anterior
        stopRecording()

        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
        try audioSession.setActive(true, options: .notifyOthersOnDeactivation)

        request = SFSpeechAudioBufferRecognitionRequest()
        guard let request = request else { throw SpeechError.requestFailed }

        let inputNode = audioEngine.inputNode
        request.shouldReportPartialResults = true

        task = recognizer.recognitionTask(with: request) { [weak self] result, error in
            Task { @MainActor in
                if let result = result {
                    self?.transcript = result.bestTranscription.formattedString
                }
                if error != nil || result?.isFinal == true {
                    let final = self?.transcript ?? ""
                    self?.stopRecording()
                    self?.onFinalTranscript?(final)
                }
            }
        }

        let format = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
            request.append(buffer)
        }

        audioEngine.prepare()
        try audioEngine.start()
        isRecording = true
    }

    /// Parar grabación
    func stopRecording() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        request?.endAudio()
        task?.cancel()
        request = nil
        task = nil
        isRecording = false
    }

    enum SpeechError: LocalizedError {
        case recognizerUnavailable
        case requestFailed
        var errorDescription: String? {
            switch self {
            case .recognizerUnavailable: return "Reconocimiento de voz no disponible"
            case .requestFailed: return "Error al iniciar solicitud de voz"
            }
        }
    }
}
