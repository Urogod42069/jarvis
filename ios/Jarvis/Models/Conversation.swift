import Foundation

struct Conversation: Identifiable, Codable {
    let id: String
    var title: String
    let updatedAt: String
    var messageCount: Int

    enum CodingKeys: String, CodingKey {
        case id, title
        case updatedAt = "updated_at"
        case messageCount = "message_count"
    }
}
