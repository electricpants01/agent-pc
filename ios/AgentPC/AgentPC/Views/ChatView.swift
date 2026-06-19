import SwiftUI

struct ChatView: View {
    @StateObject private var vm = ChatViewModel()
    @FocusState private var isInputFocused: Bool

    var body: some View {
        VStack(spacing: 0) {
            headerView

            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 8) {
                        if vm.messages.isEmpty {
                            emptyStateView
                        }
                        ForEach(vm.messages) { msg in
                            MessageBubble(
                                msg: msg,
                                isStreaming: vm.currentStreamingId == msg.id
                            )
                        }
                        Color.clear.frame(height: 1).id("bottom")
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                }
                .onChange(of: vm.messages.count) { _ in
                    withAnimation { proxy.scrollTo("bottom", anchor: .bottom) }
                }
                .onChange(of: vm.currentStreamingId) { _ in
                    withAnimation { proxy.scrollTo("bottom", anchor: .bottom) }
                }
            }
            .background(Color(.systemGroupedBackground))

            inputBar
        }
        .onAppear { vm.connect() }
        .onDisappear { vm.disconnect() }
    }

    // MARK: - Header
    private var headerView: some View {
        HStack {
            Circle()
                .fill(vm.wsService.isConnected ? Color.green : Color.red)
                .frame(width: 10, height: 10)
            Text(vm.wsService.isConnected ? "Conectado" : "Desconectado")
                .font(.caption).foregroundColor(.secondary)
            Spacer()
            if vm.isProcessing {
                ProgressView().scaleEffect(0.8)
                Text("Pensando...").font(.caption).foregroundColor(.secondary)
            }
            Button(action: { vm.clearChat() }) {
                Image(systemName: "trash").font(.caption)
            }
            .disabled(vm.messages.isEmpty)
        }
        .padding(.horizontal, 16).padding(.vertical, 8)
        .background(.ultraThinMaterial)
    }

    // MARK: - Empty State
    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Spacer().frame(height: 80)
            Image(systemName: "desktopcomputer")
                .font(.system(size: 48)).foregroundColor(.accentColor)
            Text("Agent-PC").font(.title2).bold()
            Text("Tu asistente de IA en tu máquina Linux.\nEscribe o usa el micrófono para dar comandos.")
                .multilineTextAlignment(.center).foregroundColor(.secondary)
            Spacer()
        }
        .frame(maxWidth: .infinity).padding(.top, 60)
    }

    // MARK: - Input Bar
    private var inputBar: some View {
        HStack(spacing: 10) {
            Button(action: { vm.toggleRecording() }) {
                Image(systemName: vm.speechService.isRecording ? "mic.fill" : "mic")
                    .font(.title3)
                    .foregroundColor(vm.speechService.isRecording ? .red : .accentColor)
                    .frame(width: 40, height: 40)
                    .background(Circle().fill(
                        vm.speechService.isRecording
                        ? Color.red.opacity(0.15) : Color.accentColor.opacity(0.1)
                    ))
            }
            .disabled(vm.isProcessing)

            TextField("Escribe un comando...", text: $vm.inputText, axis: .vertical)
                .focused($isInputFocused)
                .lineLimit(1...4).padding(10)
                .background(Color(.systemGray6)).cornerRadius(20)
                .submitLabel(.send)
                .onSubmit { vm.sendMessage() }

            Button(action: { vm.sendMessage() }) {
                Image(systemName: "arrow.up.circle.fill")
                    .font(.title2)
                    .foregroundColor(
                        vm.inputText.trimmingCharacters(in: .whitespaces).isEmpty
                        ? .gray : .accentColor
                    )
            }
            .disabled(vm.inputText.trimmingCharacters(in: .whitespaces).isEmpty || vm.isProcessing)
        }
        .padding(.horizontal, 12).padding(.vertical, 8)
        .background(.ultraThinMaterial)
    }
}
