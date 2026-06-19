import SwiftUI

struct MessageBubble: View {
    let msg: ChatMessage
    var isStreaming: Bool = false

    var body: some View {
        HStack(alignment: .top) {
            if msg.role == .user { Spacer(minLength: 60) }

            VStack(alignment: msg.role == .user ? .trailing : .leading, spacing: 4) {
                if msg.role == .tool {
                    HStack(spacing: 6) {
                        Image(systemName: "wrench").font(.caption)
                        Text(msg.content).font(.caption).foregroundColor(.secondary)
                    }
                    .padding(.horizontal, 10).padding(.vertical, 6)
                    .background(Color(.systemGray5)).cornerRadius(12)
                } else if msg.role == .system {
                    Text(msg.content)
                        .font(.caption).foregroundColor(.red)
                        .padding(.horizontal, 10).padding(.vertical, 6)
                        .background(Color.red.opacity(0.1)).cornerRadius(12)
                } else {
                    Text(LocalizedStringKey(msg.content))
                        .font(.body)
                        .padding(.horizontal, 14).padding(.vertical, 10)
                        .background(
                            msg.role == .user ? Color.accentColor : Color(.systemGray6)
                        )
                        .foregroundColor(msg.role == .user ? .white : .primary)
                        .cornerRadius(18)
                }

                if isStreaming {
                    HStack(spacing: 3) {
                        Circle().fill(Color.gray).frame(width: 4, height: 4)
                        Circle().fill(Color.gray).frame(width: 4, height: 4)
                        Circle().fill(Color.gray).frame(width: 4, height: 4)
                    }
                    .padding(.leading, 14)
                }

                Text(msg.timestamp, style: .time)
                    .font(.caption2).foregroundColor(.secondary)
                    .padding(.horizontal, 14)
            }

            if msg.role != .user { Spacer(minLength: 60) }
        }
    }
}
