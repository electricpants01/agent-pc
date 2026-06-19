import SwiftUI

struct SettingsView: View {
    @ObservedObject var settingsService: SettingsService

    var body: some View {
        NavigationStack {
            Form {
                Section("Servidor") {
                    HStack {
                        Text("Host").foregroundColor(.secondary)
                        TextField("192.168.x.x", text: $settingsService.settings.serverHost)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                    }
                    HStack {
                        Text("Puerto").foregroundColor(.secondary)
                        TextField("8765", text: $settingsService.settings.serverPort)
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                    }
                    Toggle("Usar SSL (wss)", isOn: $settingsService.settings.useSSL)
                }

                Section("Seguridad") {
                    SecureField("Secreto compartido", text: $settingsService.settings.authSecret)
                        .autocapitalization(.none)
                    Text("Debe coincidir con AUTH_SECRET de tu servidor.")
                        .font(.caption).foregroundColor(.secondary)
                }

                Section("Información") {
                    LabeledContent("App", value: "Agent-PC v1.0")
                    LabeledContent("Servidor esperado",
                        value: "ws://\(settingsService.settings.serverHost):\(settingsService.settings.serverPort)")
                }
            }
            .navigationTitle("Configuración")
        }
    }
}
