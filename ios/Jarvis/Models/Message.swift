import Foundation

struct Message: Identifiable, Codable {
    let id: UUID
    let role: String
    let content: String
    let createdAt: String

    var isUser: Bool { role == "user" }

    enum CodingKeys: String, CodingKey {
        case role, content
        case createdAt = "created_at"
    }

    init(id: UUID = UUID(), role: String, content: String, createdAt: String = "") {
        self.id = id
        self.role = role
        self.content = content
        self.createdAt = createdAt
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = UUID()
        self.role = try container.decode(String.self, forKey: .role)
        self.content = try container.decode(String.self, forKey: .content)
        self.createdAt = try container.decodeIfPresent(String.self, forKey: .createdAt) ?? ""
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(role, forKey: .role)
        try container.encode(content, forKey: .content)
        try container.encode(createdAt, forKey: .createdAt)
    }
}
