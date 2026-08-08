#pragma once

#include <QHBoxLayout>
#include <QJsonArray>
#include <QLabel>
#include <QPushButton>
#include <QPropertyAnimation>
#include <QScrollBar>
#include <QTextBrowser>
#include <QTextCursor>
#include <QTextEdit>
#include <QTimer>
#include <QUrl>
#include <QVBoxLayout>
#include <QVector>
#include <QWidget>

/**
 * Nexus AI Dynamic Island UI.
 *
 * The widget owns presentation only. Backend/WebSocket logic remains outside
 * this class and communicates through promptRequested() and the public slots.
 *
 * Streaming is incremental: the conversation is rendered once, then the
 * active assistant bubble is updated through a QTextCursor instead of
 * rebuilding the complete QTextDocument for every token.
 */


// Visual activity indicator. This state is intentionally independent from
// DynamicIslandWindow::State: the waveform must keep animating even when the
// user collapses the island while the AI is still generating.
class NexusIndicator final : public QWidget
{
public:
    enum class State
    {
        Idle,
        Thinking,
        Active
    };

    explicit NexusIndicator(QWidget *parent = nullptr);

    void setState(State state);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    State m_state = State::Idle;

    QTimer *m_animationTimer = nullptr;
    qreal m_phase = 0.0;
};

class DynamicIslandWindow final : public QWidget
{
    Q_OBJECT

public:
    enum class State
    {
        Idle,
        Compact,
        Input,
        Expanded
    };

    explicit DynamicIslandWindow(QWidget *parent = nullptr);
    ~DynamicIslandWindow() override = default;

    void setState(State state, bool animate = true);
    [[nodiscard]] State currentState() const noexcept { return m_state; }

public slots:
    void handleServerState(const QString &state);
    void handleToken(const QString &token);
    void handleResponseComplete(const QString &fullText);

    // Renders a task's source checklist as its own bubble in the
    // conversation. items follows the /tasks/{id}/checklist response shape:
    // [{ requirement, status, source, missing_reason }, ...].
    void handleChecklist(const QString &title, const QJsonArray &items);

signals:
    void promptRequested(const QString &text);

protected:
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void keyPressEvent(QKeyEvent *event) override;
    bool eventFilter(QObject *watched, QEvent *event) override;

private:
    struct ChatMessage
    {
        QString role;
        QString text;
    };

    // State / geometry.
    void applyRoundedMask();
    void repositionAtTopCenter();
    [[nodiscard]] QSize sizeForState(State state) const;
    void updateExpandedHeight();

    // User interaction.
    void sendCurrentPrompt();

    // Conversation rendering.
    void appendUserMessage(const QString &text);
    void appendAssistantMessage(const QString &text);
    void updateTaskProgress(const QString &title, const QJsonArray &items);
    [[nodiscard]] QString taskProgressToHtmlFragment() const;
    void renderConversation();
    void createStreamingAssistantBubble();
    void flushStreamBuffer();
    void finalizeStreamingResponse(const QString &fullText);
    void scrollToBottom();

    // Formatting.
    static QString markdownToHtmlFragment(const QString &markdown);

#ifdef Q_OS_WIN
    void enableWindowsAcrylic();
#endif

private:
    State m_state = State::Idle;

    QPropertyAnimation *m_geometryAnim = nullptr;

    QLabel *m_statusLabel = nullptr;
    NexusIndicator *m_indicator = nullptr;
    QTextBrowser *m_chatView = nullptr;
    QTextEdit *m_input = nullptr;
    QPushButton *m_sendButton = nullptr;

    QVBoxLayout *m_layout = nullptr;
    QHBoxLayout *m_inputRow = nullptr;

    // Completed conversation history. Never modified while a response is
    // being streamed; the active response lives in m_streamBuffer instead.
    QVector<ChatMessage> m_messages;

    // Current AI task progress. This is intentionally separate from the
    // conversation history so repeated checklist updates replace the same
    // progress card instead of creating multiple messages.
    QString m_taskProgressTitle;
    QJsonArray m_taskProgressItems;
    bool m_hasTaskProgress = false;

    // Tokens waiting for the next UI flush.
    QString m_streamBuffer;

    // All text inserted into the currently streaming assistant bubble.
    QString m_activeStreamText;

    // Cursor remains inside the body of the active assistant bubble.
    QTextCursor m_streamCursor;

    bool m_isStreaming = false;

    // Coalesces high-frequency backend tokens into inexpensive UI updates.
    QTimer *m_streamCoalesceTimer = nullptr;

    // Height changes are throttled separately from text updates so a long
    // response does not continuously restart the geometry animation.
    QTimer *m_heightUpdateTimer = nullptr;

    // Prevents duplicate prompt dispatch while the event loop is giving the
    // freshly-rendered user message a chance to paint.
    bool m_promptDispatchPending = false;

    static constexpr int kIdleWidth = 140;
    static constexpr int kIdleHeight = 36;

    static constexpr int kCompactWidth = 320;
    static constexpr int kCompactHeight = 56;

    static constexpr int kExpandedWidth = 420;
    static constexpr int kExpandedMinHeight = 220;
    static constexpr int kExpandedMaxHeight = 650;

    static constexpr int kCornerRadius = 20;
    static constexpr int kTopMargin = 8;

    // 30 FPS is visually smooth for text streaming while substantially
    // reducing QTextDocument/layout churn compared with 60 FPS.
    static constexpr int kStreamCoalesceMs = 33;

    // Geometry is intentionally updated less frequently than the text.
    static constexpr int kHeightUpdateMs = 100;
};