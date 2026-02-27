import Foundation

struct ChatRequest: Encodable {
    let message: String
    let stream: Bool
}

struct ChatResponse: Decodable {
    let reply: String
    let conversationId: String

    enum CodingKeys: String, CodingKey {
        case reply
        case conversationId = "conversation_id"
    }
}
