import Foundation

/// Servicio de persistencia para configuración
@MainActor
class SettingsService: ObservableObject {
    @Published var settings: AppSettings {
        didSet { save() }
    }

    private let key = "agent_pc_settings"

    init() {
        settings = SettingsService.load() ?? AppSettings()
    }

    private func save() {
        if let data = try? JSONEncoder().encode(settings) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }

    static func load() -> AppSettings? {
        guard let data = UserDefaults.standard.data(forKey: "agent_pc_settings") else {
            return nil
        }
        return try? JSONDecoder().decode(AppSettings.self, from: data)
    }
}
