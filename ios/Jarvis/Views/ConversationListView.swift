import SwiftUI

struct ConversationListView: View {
    @EnvironmentObject private var viewModel: ChatViewModel
    @State private var showSettings = false

    var body: some View {
        List {
            if viewModel.conversations.isEmpty && viewModel.errorMessage == nil {
                ContentUnavailableView(
                    "No Conversations",
                    systemImage: "bubble.left.and.bubble.right",
                    description: Text("Tap + to start chatting with Jarvis")
                )
            }

            ForEach(viewModel.conversations) { convo in
                NavigationLink(value: convo.id) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(convo.title.isEmpty ? "Untitled" : convo.title)
                            .font(.headline)
                        HStack {
                            Text("\(convo.messageCount) messages")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            Spacer()
                            Text(convo.updatedAt.prefix(16))
                                .font(.caption2)
                                .foregroundStyle(.tertiary)
                        }
                    }
                    .padding(.vertical, 4)
                }
            }
        }
        .navigationTitle("Jarvis")
        .navigationDestination(for: String.self) { conversationId in
            ChatView(conversationId: conversationId)
        }
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button {
                    showSettings = true
                } label: {
                    Image(systemName: "gear")
                }
            }
            ToolbarItem(placement: .topBarTrailing) {
                Button {
                    Task { await viewModel.createConversation() }
                } label: {
                    Image(systemName: "plus")
                }
            }
        }
        .sheet(isPresented: $showSettings) {
            SettingsView()
        }
        .task {
            await viewModel.loadConversations()
        }
        .refreshable {
            await viewModel.loadConversations()
        }
        .overlay {
            if let error = viewModel.errorMessage {
                VStack {
                    Spacer()
                    Text(error)
                        .font(.caption)
                        .foregroundStyle(.white)
                        .padding()
                        .background(.red.opacity(0.85), in: RoundedRectangle(cornerRadius: 10))
                        .padding()
                }
            }
        }
    }
}
