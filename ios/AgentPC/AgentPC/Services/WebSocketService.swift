import Foundation

@MainActor
class WebSocketService: ObservableObject {
    @Published var isConnected = false
    @Published var isStreaming = false

    private var task: URLSessionWebSocketTask?
    private var session: URLSession?
    var settings: AppSettings = AppSettings()

    var onEvent: ((ServerEvent) -> Void)?
    var onConnected: (() -> Void)?
    var onDisconnected: (() -> Void)?

    /// Conectar al servidor
    func connect() {
        let scheme = settings.useSSL ? "wss" : "ws"
        let urlString = "\(scheme)://\(settings.serverHost):\(settings.serverPort)/ws/chat"
        guard let url = URL(string: urlString) else { return }

        session = URLSession(configuration: .default)
        task = session?.webSocketTask(with: url)
        task?.resume()
        isConnected = true
        onConnected?()
        receiveMessage()
    }

    /// Desconectar
    func disconnect() {
        task?.cancel(with: .goingAway, reason: nil)
        isConnected = false
        isStreaming = false
        onDisconnected?()
    }

    /// Enviar un mensaje de chat
    func sendMessage(_ text: String, history: [[String: String]] = []) {
        // Convert ChatMessage history to the format the server expects
        let historyDicts: [[String: String]] = history.map { msg in
            ["role": msg["role"] ?? "user", "content": msg["content"] ?? ""]
        }

        let payload: [String: Any] = [
            "message": text,
            "history": historyDicts,
            "secret": settings.authSecret,
        ]

        guard let jsonData = try? JSONSerialization.data(withJSONObject: payload),
              let jsonString = String(data: jsonData, encoding: .utf8) else { return }

        isStreaming = true
        task?.send(.string(jsonString)) { [weak self] error in
            if let error = error {
                Task { @MainActor in
                    self?.onEvent?(.error("Error al enviar: \(error.localizedDescription)"))
                    self?.isStreaming = false
                }
            }
        }
    }

    /// Recibir mensajes en loop
    private func receiveMessage() {
        task?.receive { [weak self] result in
            Task { @MainActor in
                switch result {
                case .success(let message):
                    switch message {
                    case .string(let text):
                        self?.handleEvent(text)
                    case .data(let data):
                        if let text = String(data: data, encoding: .utf8) {
                            self?.handleEvent(text)
                        }
                    @unknown default:
                        break
                    }
                    self?.receiveMessage()  // seguir escuchando

                case .failure(let error):
                    self?.onEvent?(.error("WebSocket error: \(error.localizedDescription)"))
                    self?.isConnected = false
                    self?.isStreaming = false
                    self?.onDisconnected?()
                }
            }
        }
    }

    /// Parsear un evento JSON del servidor
    private func handleEvent(_ raw: String) {
        guard let data = raw.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = json["type"] as? String else {
            // Podría ser un mensaje no-JSON; intentar parsear como SSE
            if raw.hasPrefix("text: ") {
                onEvent?(.text(String(raw.dropFirst(6))))
            }
            return
        }

        switch type {
        case "text":
            if let content = json["content"] as? String {
                onEvent?(.text(content))
            }
        case "tool":
            if let tc = json["content"] as? [String: Any],
               let id = tc["id"] as? String,
               let name = tc["name"] as? String {
                let args = tc["arguments"] as? String ?? ""
                onEvent?(.tool(ToolCall(id: id, name: name, arguments: args)))
            }
        case "tool_result":
            if let tr = json["content"] as? [String: Any] {
                let summary = describeToolResult(tr)
                onEvent?(.toolResult(ToolResult(ok: tr["ok"] as? Bool ?? false,
                                                content: summary)))
            }
        case "error":
            let content = json["content"] as? String ?? "Error desconocido"
            onEvent?(.error(content))
        case "done":
            isStreaming = false
            onEvent?(.done)
        default:
            break
        }
    }

    /// Resumir un tool result para mostrar en la UI
    private func describeToolResult(_ result: [String: Any]) -> String {
        if let ok = result["ok"] as? Bool, !ok {
            return result["error"] as? String ?? "Error"
        }

        // Intentar dar un resumen útil según el tipo de resultado
        if let path = result["path"] as? String, result["content"] is String {
            return "✅ Archivo leído: \(path)"
        }
        if let path = result["path"] as? String, let bytes = result["bytes_written"] as? Int {
            return "✅ Escrito: \(path) (\(bytes) bytes)"
        }
        if let cmd = result["command"] as? String {
            let stdout = result["stdout"] as? String ?? ""
            let preview = String(stdout.prefix(300))
            return "💻 \(cmd)\n\(preview)"
        }
        if let path = result["path"] as? String, let items = result["items"] as? [String] {
            return "📁 \(path)\n\(items.prefix(10).joined(separator: "\n"))"
        }
        if let matches = result["matches"] as? [String] {
            return "🔍 Encontrados: \(result["count"] as? Int ?? matches.count) coincidencias"
        }

        return "✅ Completado"
    }
}
