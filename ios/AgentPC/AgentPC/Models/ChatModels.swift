import Foundation

/// Un mensaje del chat
struct ChatMessage: Identifiable, Codable {
    let id: UUID
    let role: MessageRole      // "user", "assistant", "tool"
    let content: String
    let timestamp: Date
    var toolCall: ToolCall?
    var toolResult: ToolResult?

    init(id: UUID = UUID(),
         role: MessageRole,
         content: String,
         timestamp: Date = Date(),
         toolCall: ToolCall? = nil,
         toolResult: ToolResult? = nil) {
        self.id = id
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.toolCall = toolCall
        self.toolResult = toolResult
    }
}

enum MessageRole: String, Codable {
    case user
    case assistant
    case tool
    case system
}

/// Una llamada a herramienta hecha por el agente
struct ToolCall: Codable {
    let id: String
    let name: String
    let arguments: String
}

/// Resultado de una herramienta
struct ToolResult: Codable {
    let ok: Bool
    let content: String
}

/// Eventos recibidos por WebSocket del servidor
enum ServerEvent {
    case text(String)
    case tool(ToolCall)
    case toolResult(ToolResult)
    case error(String)
    case done
}

/// Configuración persistente del usuario
struct AppSettings: Codable {
    var serverHost: String = "192.168.1.100"
    var serverPort: String = "8765"
    var authSecret: String = "agent-pc-local-secret-change-me"
    var useSSL: Bool = false
}
