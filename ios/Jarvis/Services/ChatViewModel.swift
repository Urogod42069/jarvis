import Foundation
import SwiftUI

@MainActor
final class ChatViewModel: ObservableObject {
    @Published var conversations: [Conversation] = []
    @Published var currentConversationId: String?
    @Published var messages: [Message] = []
    @Published var isLoading = false
    @Published var streamingText = ""
    @Published var errorMessage: String?

    /// Persisted server URL — defaults to localhost for simulator.
    @AppStorage("serverURL") var serverURL: String = "http://localhost:8000" {
        didSet { updateBaseURL() }
    }

    private let api = JarvisAPIClient.shared

    init() {
        updateBaseURL()
    }

    private func updateBaseURL() {
        if let url = URL(string: serverURL) {
            api.baseURL = url
        }
    }

    // MARK: - Conversations

    func loadConversations() async {
        do {
            conversations = try await api.listConversations()
            errorMessage = nil
        } catch {
            errorMessage = "Failed to load conversations: \(error.localizedDescription)"
        }
    }

    func createConversation() async -> String? {
        do {
            let convo = try await api.createConversation()
            conversations.insert(convo, at: 0)
            currentConversationId = convo.id
            messages = []
            errorMessage = nil
            return convo.id
        } catch {
            errorMessage = "Failed to create conversation: \(error.localizedDescription)"
            return nil
        }
    }

    func selectConversation(_ id: String) async {
        currentConversationId = id
        await loadMessages(for: id)
    }

    func loadMessages(for conversationId: String) async {
        do {
            messages = try await api.getMessages(conversationId: conversationId)
            errorMessage = nil
        } catch {
            errorMessage = "Failed to load messages: \(error.localizedDescription)"
        }
    }

    // MARK: - Chat

    func send(_ text: String) async {
        guard let conversationId = currentConversationId else { return }
        guard !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }

        let userMessage = Message(role: "user", content: text)
        messages.append(userMessage)
        isLoading = true
        streamingText = ""

        do {
            let reply = try await api.sendMessageStreaming(
                text,
                conversationId: conversationId
            ) { [weak self] chunk in
                Task { @MainActor in
                    self?.streamingText += chunk
                }
            }

            // Replace streaming text with final message
            streamingText = ""
            let assistantMessage = Message(role: "assistant", content: reply)
            messages.append(assistantMessage)
            errorMessage = nil
        } catch {
            streamingText = ""
            errorMessage = "Failed to send message: \(error.localizedDescription)"
        }

        isLoading = false
    }
}
