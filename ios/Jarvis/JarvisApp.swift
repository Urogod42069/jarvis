import SwiftUI

@main
struct JarvisApp: App {
    @StateObject private var chatViewModel = ChatViewModel()

    var body: some Scene {
        WindowGroup {
            NavigationStack {
                ConversationListView()
            }
            .environmentObject(chatViewModel)
        }
    }
}
