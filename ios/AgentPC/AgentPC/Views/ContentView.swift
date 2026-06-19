import SwiftUI

struct ContentView: View {
    @StateObject private var settingsService = SettingsService()

    var body: some View {
        TabView {
            ChatView()
                .tabItem {
                    Label("Chat", systemImage: "message.fill")
                }

            SettingsView(settingsService: settingsService)
                .tabItem {
                    Label("Ajustes", systemImage: "gear")
                }
        }
    }
}
