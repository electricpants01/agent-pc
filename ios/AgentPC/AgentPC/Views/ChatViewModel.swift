import Foundation
import Combine

@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var inputText: String = ""
    @Published var isProcessing = false
    @Published var currentStreamingId: UUID?

    let wsService = WebSocketService()
    let speechService = SpeechService()
    let settingsService = SettingsService()

    private var cancellables = Set<AnyCancellable>()

    init() {
        // Sincronizar settings con WebSocket
        wsService.settings = settingsService.settings

        // Manejar eventos del servidor
        wsService.onEvent = { [weak self] event in
            Task { @MainActor in
                self?.handleServerEvent(event)
            }
        }

        // Voice: cuando termina de transcribir, enviar
        speechService.onFinalTranscript = { [weak self] text in
            Task { @MainActor in
                guard let self = self, !text.trimmingCharacters(in: .whitespaces).isEmpty else { return }
                self.inputText = text
                self.sendMessage()
            }
        }
    }

    /// Conectar al servidor
    func connect() {
        wsService.settings = settingsService.settings
        wsService.connect()
    }

    func disconnect() {
        wsService.disconnect()
    }

    /// Enviar mensaje de texto
    func sendMessage() {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }

        // Añadir mensaje del usuario
        let userMsg = ChatMessage(role: .user, content: text)
        messages.append(userMsg)
        inputText = ""
        isProcessing = true

        // Conectar si no está conectado
        if !wsService.isConnected {
            connect()
            // Dar un momento para conectar
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
                self?.wsService.sendMessage(text, history: self?.buildHistory() ?? [])
            }
        } else {
            wsService.sendMessage(text, history: buildHistory())
        }
    }

    /// Construir historial para enviar al servidor (últimos 20 mensajes)
    private func buildHistory() -> [[String: String]] {
        let last = messages.suffix(20)
        return last.compactMap { msg in
            // Solo incluir user y assistant, no tool messages internos
            if msg.role == .user || msg.role == .assistant {
                return ["role": msg.role.rawValue, "content": msg.content]
            }
            return nil
        }
    }

    /// Iniciar/cancelar grabación de voz
    func toggleRecording() {
        if speechService.isRecording {
            speechService.stopRecording()
        } else {
            Task {
                await speechService.requestAuthorization()
                if speechService.isAuthorized {
                    try? speechService.startRecording()
                }
            }
        }
    }

    /// Manejar eventos del servidor
    private func handleServerEvent(_ event: ServerEvent) {
        switch event {
        case .text(let chunk):
            if let sid = currentStreamingId,
               let idx = messages.firstIndex(where: { $0.id == sid }) {
                messages[idx].content += chunk
            } else {
                let newMsg = ChatMessage(role: .assistant, content: chunk)
                currentStreamingId = newMsg.id
                messages.append(newMsg)
            }

        case .tool(let toolCall):
            let msg = ChatMessage(
                role: .tool,
                content: "🔧 \(toolCall.name)",
                toolCall: toolCall
            )
            messages.append(msg)

        case .toolResult(let result):
            // Añadir resultado como nota debajo del tool call
            if let lastIdx = messages.lastIndex(where: { $0.role == .tool }) {
                let summary = result.content
                let resultMsg = ChatMessage(role: .tool, content: summary)
                messages.append(resultMsg)
            }

        case .error(let err):
            let msg = ChatMessage(role: .system, content: "❌ \(err)")
            messages.append(msg)
            isProcessing = false
            currentStreamingId = nil

        case .done:
            isProcessing = false
            currentStreamingId = nil
        }
    }

    /// Limpiar chat
    func clearChat() {
        messages.removeAll()
        currentStreamingId = nil
    }
}
