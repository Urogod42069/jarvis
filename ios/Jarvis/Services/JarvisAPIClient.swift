import Foundation

/// Handles all HTTP communication with the Jarvis FastAPI backend.
final class JarvisAPIClient {
    static let shared = JarvisAPIClient()

    /// Base URL for the Jarvis API. Change this to your server's address.
    /// For the iOS Simulator talking to a local server, use localhost.
    /// For a physical device, use your Mac's LAN IP address.
    var baseURL: URL

    private let session: URLSession
    private let decoder: JSONDecoder

    init(baseURL: URL = URL(string: "http://localhost:8000")!) {
        self.baseURL = baseURL
        self.session = URLSession(configuration: .default)
        self.decoder = JSONDecoder()
    }

    // MARK: - Conversations

    func listConversations(limit: Int = 20) async throws -> [Conversation] {
        var components = URLComponents(url: baseURL.appendingPathComponent("/api/conversations"), resolvingAgainstBaseURL: false)!
        components.queryItems = [URLQueryItem(name: "limit", value: "\(limit)")]
        let (data, _) = try await session.data(from: components.url!)
        return try decoder.decode([Conversation].self, from: data)
    }

    func createConversation(title: String = "") async throws -> Conversation {
        var components = URLComponents(url: baseURL.appendingPathComponent("/api/conversations"), resolvingAgainstBaseURL: false)!
        if !title.isEmpty {
            components.queryItems = [URLQueryItem(name: "title", value: title)]
        }
        var request = URLRequest(url: components.url!)
        request.httpMethod = "POST"
        let (data, _) = try await session.data(for: request)
        return try decoder.decode(Conversation.self, from: data)
    }

    func getMessages(conversationId: String) async throws -> [Message] {
        let url = baseURL.appendingPathComponent("/api/conversations/\(conversationId)/messages")
        let (data, _) = try await session.data(from: url)
        return try decoder.decode([Message].self, from: data)
    }

    // MARK: - Chat

    func sendMessage(_ text: String, conversationId: String) async throws -> ChatResponse {
        let url = baseURL.appendingPathComponent("/api/conversations/\(conversationId)/chat")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = ChatRequest(message: text, stream: false)
        request.httpBody = try JSONEncoder().encode(body)

        let (data, _) = try await session.data(for: request)
        return try decoder.decode(ChatResponse.self, from: data)
    }

    /// Send a message and stream the reply via SSE.
    /// Calls `onChunk` for each text chunk, then returns the full assembled reply.
    func sendMessageStreaming(
        _ text: String,
        conversationId: String,
        onChunk: @escaping (String) -> Void
    ) async throws -> String {
        let url = baseURL.appendingPathComponent("/api/conversations/\(conversationId)/chat")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = ChatRequest(message: text, stream: true)
        request.httpBody = try JSONEncoder().encode(body)

        let (bytes, _) = try await session.bytes(for: request)
        var fullReply = ""

        for try await line in bytes.lines {
            if line.hasPrefix("data: ") {
                let payload = String(line.dropFirst(6))
                if payload == "[DONE]" { break }
                fullReply += payload
                onChunk(payload)
            }
        }

        return fullReply
    }

    // MARK: - One-shot chat

    func chatOneShot(_ text: String) async throws -> ChatResponse {
        let url = baseURL.appendingPathComponent("/api/chat")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = ChatRequest(message: text, stream: false)
        request.httpBody = try JSONEncoder().encode(body)

        let (data, _) = try await session.data(for: request)
        return try decoder.decode(ChatResponse.self, from: data)
    }
}
