#include "DynamicIslandWindow.h"

#include <QApplication>
#include <QDesktopServices>
#include <QPainter>
#include <QPainterPath>
#include <QMouseEvent>
#include <QKeyEvent>
#include <QEasingCurve>
#include <QTextDocument>
#include <QTextTable>
#include <QTextTableCell>
#include <QTextTableCellFormat>
#include <QTextTableFormat>
#include <QRegularExpression>
#include <QJsonObject>
#include <QJsonValue>
#include <utility>
#include <QDebug>
#include <cmath>
#ifdef Q_OS_WIN
#include <windows.h>
#include <dwmapi.h>
#pragma comment(lib, "dwmapi.lib")

namespace
{
enum WINDOWCOMPOSITIONATTRIB
{
    WCA_ACCENT_POLICY = 19
};

struct WINDOWCOMPOSITIONATTRIBDATA
{
    WINDOWCOMPOSITIONATTRIB Attrib;
    PVOID pvData;
    SIZE_T cbData;
};

enum ACCENT_STATE
{
    ACCENT_DISABLED = 0,
    ACCENT_ENABLE_GRADIENT = 1,
    ACCENT_ENABLE_TRANSPARENTGRADIENT = 2,
    ACCENT_ENABLE_BLURBEHIND = 3,
    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4,
    ACCENT_ENABLE_HOSTBACKDROP = 5
};

struct ACCENT_POLICY
{
    ACCENT_STATE AccentState;
    DWORD AccentFlags;
    DWORD GradientColor;
    DWORD AnimationId;
};

using SetWindowCompositionAttributeFn = BOOL(WINAPI *)(HWND, WINDOWCOMPOSITIONATTRIBDATA *);

constexpr DWORD kDwmwaWindowCornerPreference = 33;
constexpr DWORD kDwmwcpRound = 2;
} // namespace
#endif

namespace
{
// Inserts a message as an explicit one-row table. QTextDocument's HTML/CSS
// support is intentionally limited; using tables makes each message an
// unambiguous block and avoids CSS margin/layout races between bubbles.
QTextCursor insertMessageBubble(QTextCursor cursor,
                                const QString &label,
                                const QString &labelColor,
                                const QString &background,
                                bool rightAligned,
                                const QString &bodyHtml,
                                QTextCursor *bodyCursor = nullptr)
{
    QTextTableFormat tableFormat;
    tableFormat.setBorder(0);
    tableFormat.setCellPadding(0);
    tableFormat.setCellSpacing(0);
    tableFormat.setWidth(QTextLength(QTextLength::PercentageLength, 100));
    tableFormat.setTopMargin(0);
    tableFormat.setBottomMargin(8);
    tableFormat.setLeftMargin(rightAligned ? 32 : 0);
    tableFormat.setRightMargin(rightAligned ? 0 : 32);

    QTextTable *table = cursor.insertTable(1, 1, tableFormat);
    QTextTableCell cell = table->cellAt(0, 0);

    QTextTableCellFormat cellFormat;
    cellFormat.setBackground(QColor(background));
    cellFormat.setTopPadding(8);
    cellFormat.setBottomPadding(8);
    cellFormat.setLeftPadding(12);
    cellFormat.setRightPadding(12);
    cell.setFormat(cellFormat);

    QTextCursor cellCursor = cell.firstCursorPosition();

    QTextCharFormat labelFormat;
    labelFormat.setForeground(QColor(labelColor));
    labelFormat.setFontWeight(QFont::DemiBold);
    labelFormat.setFontPointSize(9);
    cellCursor.insertText(label, labelFormat);
    cellCursor.insertBlock();

    if (bodyCursor)
        *bodyCursor = cellCursor;

    if (!bodyHtml.isEmpty())
        cellCursor.insertHtml(bodyHtml);

    // Put the document cursor immediately after the table so the next
    // message can only be inserted after this complete block.
    QTextCursor afterTable = table->lastCursorPosition();
    afterTable.movePosition(QTextCursor::NextBlock);
    return afterTable;
}

QString escapeStreamingText(const QString &text)
{
    return text.toHtmlEscaped().replace(QLatin1Char('\n'), QStringLiteral("<br>"));
}
} // namespace
NexusIndicator::NexusIndicator(QWidget *parent)
    : QWidget(parent)
{
    setFixedSize(20, 16);

    m_animationTimer = new QTimer(this);
    m_animationTimer->setInterval(40);

    connect(m_animationTimer, &QTimer::timeout, this, [this]()
    {
        m_phase += 0.22;

        if (m_phase > 1000.0)
            m_phase = 0.0;

        update();
    });
}

void NexusIndicator::setState(State state)
{
    if (m_state == state)
        return;

    m_state = state;

    if (m_state == State::Thinking)
    {
        if (!m_animationTimer->isActive())
            m_animationTimer->start();
    }
    else
    {
        m_animationTimer->stop();
        m_phase = 0.0;
    }

    update();
}

void NexusIndicator::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);

    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    const QPointF center(width() / 2.0, height() / 2.0);

    if (m_state == State::Idle)
    {
        painter.setBrush(QColor("#55D68A"));
        painter.setPen(Qt::NoPen);

        painter.drawEllipse(center, 4.0, 4.0);
        return;
    }

    if (m_state == State::Active)
    {
        painter.setBrush(QColor("#FF9F43"));
        painter.setPen(Qt::NoPen);

        painter.drawEllipse(center, 4.0, 4.0);
        return;
    }

    // ---------------------------------------------------------
    // Thinking / generating waveform
    // ---------------------------------------------------------

    painter.setPen(Qt::NoPen);
    painter.setBrush(QColor("#FF9F43"));

    constexpr int barCount = 5;
    constexpr qreal barWidth = 2.0;
    constexpr qreal spacing = 1.5;

    const qreal totalWidth =
        barCount * barWidth +
        (barCount - 1) * spacing;

    const qreal startX =
        (width() - totalWidth) / 2.0;

    for (int i = 0; i < barCount; ++i)
    {
        const qreal wave =
            (std::sin(m_phase + i * 0.8) + 1.0) * 0.5;

        const qreal barHeight =
            3.0 + wave * 8.0;

        const qreal x =
            startX + i * (barWidth + spacing);

        const qreal y =
            (height() - barHeight) / 2.0;

        painter.drawRoundedRect(
            QRectF(x, y, barWidth, barHeight),
            1.0,
            1.0
        );
    }
}
DynamicIslandWindow::DynamicIslandWindow(QWidget *parent)
    : QWidget(parent)
{
    setWindowFlags(Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint | Qt::Tool);
    setAttribute(Qt::WA_TranslucentBackground);
    setAttribute(Qt::WA_NoSystemBackground);

    m_layout = new QVBoxLayout(this);
    m_layout->setContentsMargins(16, 8, 16, 8);
    m_layout->setSpacing(6);

    auto *headerLayout = new QHBoxLayout();
    headerLayout->setContentsMargins(0, 0, 0, 0);
    headerLayout->setSpacing(7);
    m_statusLabel = new QLabel(QStringLiteral("Nexus AI"), this);
    m_statusLabel->setStyleSheet(
        QStringLiteral("color:white;font-size:13px;font-weight:600;background:transparent;"));

    m_indicator = new NexusIndicator(this);

    headerLayout->addWidget(m_statusLabel);
    headerLayout->addWidget(m_indicator, 0, Qt::AlignVCenter);
    headerLayout->addStretch();

    m_layout->addLayout(headerLayout);

    m_chatView = new QTextBrowser(this);
    m_chatView->setFrameShape(QFrame::NoFrame);
    m_chatView->setReadOnly(true);
    m_chatView->setOpenExternalLinks(true);
    m_chatView->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
    m_chatView->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    m_chatView->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    m_chatView->document()->setDocumentMargin(8);
    m_chatView->setStyleSheet(R"(
        QTextBrowser {
            background: transparent;
            border: none;
            color: white;
            font-size: 13px;
        }
    )");
    // Detect when the user scrolls away from the bottom during streaming.
    // Programmatic scrolling from scrollToBottom() is explicitly ignored.
    connect(m_chatView->verticalScrollBar(), &QScrollBar::valueChanged,
            this, [this](int value)
    {
        if (m_programmaticScroll)
            return;

        QScrollBar *bar = m_chatView->verticalScrollBar();
        if (!bar)
            return;

        if (value >= bar->maximum())
        {
            m_userScrolledUp = false;
        }
        else if (m_isStreaming)
        {
            m_userScrolledUp = true;
        }
    });

    m_chatView->hide();
    m_layout->addWidget(m_chatView, 1);

    m_input = new QTextEdit(this);
    m_input->setPlaceholderText(QStringLiteral("Ask Nexus AI..."));
    m_input->setFrameShape(QFrame::NoFrame);
    m_input->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
    m_input->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    m_input->setFixedHeight(36);
    m_input->setMaximumHeight(90);
    m_input->setStyleSheet(R"(
        QTextEdit {
            background: transparent;
            color: white;
            border: none;
            font-size: 14px;
        }
    )");
    m_input->installEventFilter(this);
    m_input->hide();

    m_sendButton = new QPushButton(QString::fromUtf8("\xE2\x9E\xA4"), this);
    m_sendButton->setFixedSize(32, 32);
    m_sendButton->setCursor(Qt::PointingHandCursor);
    m_sendButton->setStyleSheet(R"(
        QPushButton {
            background: rgba(255,255,255,0.10);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 14px;
        }
        QPushButton:hover { background: rgba(255,255,255,0.18); }
    )");
    m_sendButton->hide();
    connect(m_sendButton, &QPushButton::clicked,
            this, &DynamicIslandWindow::sendCurrentPrompt);

    m_inputRow = new QHBoxLayout();
    m_inputRow->setContentsMargins(0, 0, 0, 0);
    m_inputRow->setSpacing(8);
    m_inputRow->addWidget(m_input, 1);
    m_inputRow->addWidget(m_sendButton, 0, Qt::AlignBottom);
    m_layout->addLayout(m_inputRow);

    m_geometryAnim = new QPropertyAnimation(this, "geometry", this);
    m_geometryAnim->setDuration(320);
    m_geometryAnim->setEasingCurve(QEasingCurve::OutExpo);

    m_streamCoalesceTimer = new QTimer(this);
    m_streamCoalesceTimer->setSingleShot(true);
    connect(m_streamCoalesceTimer, &QTimer::timeout,
            this, &DynamicIslandWindow::flushStreamBuffer);

    m_heightUpdateTimer = new QTimer(this);
    m_heightUpdateTimer->setSingleShot(true);
    connect(m_heightUpdateTimer, &QTimer::timeout,
            this, &DynamicIslandWindow::updateExpandedHeight);

    setState(State::Idle, false);
    repositionAtTopCenter();

#ifdef Q_OS_WIN
    QTimer::singleShot(0, this, [this]() { enableWindowsAcrylic(); });
#endif
}

void DynamicIslandWindow::setState(State state, bool animate)
{
    m_state = state;
    const QSize target = sizeForState(state);

    QRect newGeo(0, 0, target.width(), target.height());
    if (screen())
    {
        const QRect avail = screen()->availableGeometry();
        newGeo.moveLeft(avail.center().x() - target.width() / 2);
        newGeo.moveTop(avail.top() + kTopMargin);
    }

    switch (state)
    {
    case State::Idle:
    m_chatView->hide();
    m_input->hide();
    m_sendButton->hide();
    m_input->clear();

    m_statusLabel->setText(QStringLiteral("Nexus AI"));

    break;

    case State::Compact:
    m_chatView->hide();
    m_input->hide();
    m_sendButton->hide();

    m_statusLabel->setText(QStringLiteral("Nexus AI"));

    break;

    case State::Input:
    m_chatView->show();
    m_input->show();
    m_sendButton->show();

    m_statusLabel->setText(QStringLiteral("Nexus AI"));

    m_input->setFocus();

    break;

    case State::Expanded:
        m_chatView->show();
        m_input->show();
        m_sendButton->show();
        m_statusLabel->setText(QStringLiteral("Nexus AI"));
        break;
    }

    if (animate && isVisible())
    {
        m_geometryAnim->stop();
        m_geometryAnim->setStartValue(geometry());
        m_geometryAnim->setEndValue(newGeo);
        m_geometryAnim->start();
    }
    else
    {
        setGeometry(newGeo);
    }

    if (state == State::Input || state == State::Expanded)
    {
        if (m_heightUpdateTimer->isActive())
            m_heightUpdateTimer->stop();
        updateExpandedHeight();
    }
}

QSize DynamicIslandWindow::sizeForState(State state) const
{
    switch (state)
    {
    case State::Idle:
        return QSize(kIdleWidth, kIdleHeight);
    case State::Compact:
        return QSize(kCompactWidth, kCompactHeight);
    case State::Input:
    case State::Expanded:
        return QSize(kExpandedWidth, kExpandedMinHeight);
    }
    return QSize(kIdleWidth, kIdleHeight);
}

void DynamicIslandWindow::repositionAtTopCenter()
{
    if (!screen())
        return;

    const QRect avail = screen()->availableGeometry();
    move(avail.center().x() - width() / 2, avail.top() + kTopMargin);
}

void DynamicIslandWindow::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);

    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    QPainterPath path;
    path.addRoundedRect(rect(), kCornerRadius, kCornerRadius);
    painter.fillPath(path, QColor(20, 20, 24, 200));
}

void DynamicIslandWindow::resizeEvent(QResizeEvent *event)
{
    QWidget::resizeEvent(event);
    applyRoundedMask();
}

void DynamicIslandWindow::applyRoundedMask()
{
    QPainterPath path;
    path.addRoundedRect(rect(), kCornerRadius, kCornerRadius);
    setMask(QRegion(path.toFillPolygon().toPolygon()));
}

void DynamicIslandWindow::mousePressEvent(QMouseEvent *event)
{
    if (event->button() != Qt::LeftButton)
    {
        QWidget::mousePressEvent(event);
        return;
    }

    switch (m_state)
    {
    case State::Idle:
    case State::Compact:
        setState(State::Input, true);
        break;
    case State::Input:
    case State::Expanded:
        setState(State::Idle, true);
        break;
    }
}

void DynamicIslandWindow::keyPressEvent(QKeyEvent *event)
{
    if (event->key() == Qt::Key_Escape && m_state != State::Idle)
    {
        setState(State::Idle, true);
        return;
    }

    QWidget::keyPressEvent(event);
}

bool DynamicIslandWindow::eventFilter(QObject *watched, QEvent *event)
{
    if (watched == m_input && event->type() == QEvent::KeyPress)
    {
        auto *keyEvent = static_cast<QKeyEvent *>(event);
        const bool isEnter = keyEvent->key() == Qt::Key_Return ||
                             keyEvent->key() == Qt::Key_Enter;

        if (isEnter && !(keyEvent->modifiers() & Qt::ShiftModifier))
        {
            sendCurrentPrompt();
            return true;
        }
    }

    return QWidget::eventFilter(watched, event);
}

void DynamicIslandWindow::sendCurrentPrompt()
{
    if (!m_input->isEnabled() || m_promptDispatchPending)
        return;

    const QString prompt = m_input->toPlainText().trimmed();
    if (prompt.isEmpty())
        return;

    if (m_state != State::Input && m_state != State::Expanded)
        setState(State::Input, true);

    qDebug() << "Emitting prompt:" << prompt;

    // A new turn starts at the newest message.
    m_userScrolledUp = false;
    appendUserMessage(prompt);
    m_input->clear();
    m_input->setEnabled(false);
    m_statusLabel->setText(QStringLiteral("Nexus AI"));
    m_indicator->setState(NexusIndicator::State::Thinking);
    m_promptDispatchPending = true;

    // Let Qt paint the complete user bubble before backend work can produce
    // the first assistant token. This removes the visual race where the two
    // messages can appear in the same layout pass.
    QTimer::singleShot(0, this, [this, prompt]()
    {
        m_promptDispatchPending = false;
        emit promptRequested(prompt);
    });
}

void DynamicIslandWindow::appendUserMessage(const QString &text)
{
    m_messages.append({QStringLiteral("user"), text});
    renderConversation();
}

void DynamicIslandWindow::appendAssistantMessage(const QString &text)
{
    m_messages.append({QStringLiteral("assistant"), text});
    m_streamBuffer.clear();
    m_activeStreamText.clear();
    m_isStreaming = false;
    m_streamCursor = QTextCursor();
    renderConversation();
}

void DynamicIslandWindow::updateTaskProgress(const QString &title,
                                             const QJsonArray &items)
{
    m_taskProgressTitle = title;
    m_taskProgressItems = items;
    m_hasTaskProgress = true;

    // The progress card is part of the stable UI, so simply re-rendering
    // keeps it synchronized with the latest backend checklist state.
    renderConversation();

    if (!m_heightUpdateTimer->isActive())
        m_heightUpdateTimer->start(kHeightUpdateMs);
}

QString DynamicIslandWindow::taskProgressToHtmlFragment() const
{
    int total = 0;
    int complete = 0;

    for (const QJsonValue &value : m_taskProgressItems)
    {
        const QJsonObject item = value.toObject();
        const QString status =
            item.value(QStringLiteral("status")).toString();

        if (status == QLatin1String("not_applicable"))
            continue;

        ++total;

        if (status == QLatin1String("complete"))
            ++complete;
    }

    const int percent =
        total > 0
            ? qRound((complete / static_cast<qreal>(total)) * 100.0)
            : 0;

    QString html;

    // Header
    html += QStringLiteral(
        "<table width='100%' cellspacing='0' cellpadding='0'>"
        "<tr>"
        "<td>"
        "<span style='color:#ffd479;font-size:12px;font-weight:600;'>"
        "AI TASK PROGRESS"
        "</span>"
        "</td>"
        "<td align='right'>"
        "<span style='color:white;font-size:12px;'>"
        "%1 / %2"
        "</span>"
        "</td>"
        "</tr>"
        "</table>"
    ).arg(complete).arg(total);

    // Progress bar background + filled portion.
    html += QStringLiteral(
        "<table width='100%' cellspacing='0' cellpadding='0' "
        "style='margin-top:8px;'>"
        "<tr>"
        "<td bgcolor='#35353b' height='6'>"
        "<table width='%1%' cellspacing='0' cellpadding='0'>"
        "<tr><td bgcolor='#ffd479' height='6'></td></tr>"
        "</table>"
        "</td>"
        "</tr>"
        "</table>"
    ).arg(percent);

    // Percentage
    html += QStringLiteral(
        "<div style='margin-top:6px;"
        "color:#a8a8ad;"
        "font-size:11px;'>"
        "%1% complete"
        "</div>"
    ).arg(percent);

    // Task title, if the backend supplied one.
    if (!m_taskProgressTitle.isEmpty())
    {
        html += QStringLiteral(
            "<div style='margin-top:8px;"
            "color:#d8d8dc;"
            "font-size:11px;'>"
            "%1"
            "</div>"
        ).arg(m_taskProgressTitle.toHtmlEscaped());
    }

    // Individual task steps.
    html += QStringLiteral(
        "<div style='margin-top:8px;'>"
    );

    for (const QJsonValue &value : m_taskProgressItems)
    {
        const QJsonObject item = value.toObject();

        const QString status =
            item.value(QStringLiteral("status")).toString();

        if (status == QLatin1String("not_applicable"))
            continue;

        const QString requirement =
            item.value(QStringLiteral("requirement"))
                .toString()
                .toHtmlEscaped();

        const bool isComplete =
            status == QLatin1String("complete");

        const QString glyph = isComplete
            ? QStringLiteral("&#10003;")
            : QStringLiteral("&#9675;");

        const QString glyphColor = isComplete
            ? QStringLiteral("#55D68A")
            : QStringLiteral("#77777f");

        html += QStringLiteral(
            "<div style='margin-top:4px;'>"
            "<span style='color:%1;font-size:12px;'>%2</span>"
            "&nbsp;"
            "<span style='color:#d8d8dc;font-size:11px;'>%3</span>"
            "</div>"
        ).arg(glyphColor, glyph, requirement);
    }

    html += QStringLiteral("</div>");

    return html;
}

QString DynamicIslandWindow::markdownToHtmlFragment(const QString &markdown)
{
    QTextDocument doc;
    doc.setMarkdown(markdown);
    const QString html = doc.toHtml();

    static const QRegularExpression bodyRe(
        QStringLiteral("<body[^>]*>([\\s\\S]*)</body>"));
    const auto match = bodyRe.match(html);
    return match.hasMatch() ? match.captured(1) : markdown.toHtmlEscaped();
}

void DynamicIslandWindow::renderConversation()
{
    // Preserve the user's viewport if they deliberately scrolled upward.
    const bool shouldFollowBottom = !m_userScrolledUp;

    // A complete render is only used when the stable conversation changes
    // (for example after a user message, a completed assistant response,
    // or an updated AI task-progress state).
    m_chatView->setUpdatesEnabled(false);
    m_chatView->clear();

    QTextCursor cursor = m_chatView->textCursor();
    QTextDocument *doc = m_chatView->document();
    doc->clear();
    cursor = QTextCursor(doc);

    // Task progress is UI state, not conversation history. Always render
    // the latest progress card before the conversation messages.
    if (m_hasTaskProgress)
    {
        cursor = insertMessageBubble(
            cursor,
            QStringLiteral("Nexus"),
            QStringLiteral("#ffd479"),
            QColor(255, 255, 255, 13).name(QColor::HexArgb),
            false,
            taskProgressToHtmlFragment());
    }

    for (int i = 0; i < m_messages.size(); ++i)
    {
        const ChatMessage &msg = m_messages[i];
        const bool isUser = msg.role == QLatin1String("user");

        if (isUser)
        {
            cursor = insertMessageBubble(
                cursor,
                QStringLiteral("You"),
                QStringLiteral("#9ecbff"),
                QColor(255, 255, 255, 26).name(QColor::HexArgb),
                true,
                msg.text.toHtmlEscaped().replace(QLatin1Char('\n'), QStringLiteral("<br>")));
        }
        else
        {
            cursor = insertMessageBubble(
                cursor,
                QStringLiteral("Nexus"),
                QStringLiteral("#b9f6c8"),
                QColor(255, 255, 255, 13).name(QColor::HexArgb),
                false,
                markdownToHtmlFragment(msg.text));
        }
    }

    m_chatView->setUpdatesEnabled(true);
    m_chatView->viewport()->update();

    if (shouldFollowBottom)
        scrollToBottom();

    updateExpandedHeight();
}

void DynamicIslandWindow::createStreamingAssistantBubble()
{
    if (m_isStreaming)
        return;

    // The stable conversation is already rendered. Append exactly one
    // assistant table and keep a cursor inside its body forever during this
    // response.
    QTextCursor cursor(m_chatView->document());
    cursor.movePosition(QTextCursor::End);

    QTextTableFormat tableFormat;
    tableFormat.setBorder(0);
    tableFormat.setCellPadding(0);
    tableFormat.setCellSpacing(0);
    tableFormat.setWidth(QTextLength(QTextLength::PercentageLength, 100));
    tableFormat.setBottomMargin(8);
    tableFormat.setRightMargin(32);

    QTextTable *table = cursor.insertTable(1, 1, tableFormat);
    QTextTableCell cell = table->cellAt(0, 0);

    QTextTableCellFormat cellFormat;
    cellFormat.setBackground(QColor(255, 255, 255, 13));
    cellFormat.setTopPadding(8);
    cellFormat.setBottomPadding(8);
    cellFormat.setLeftPadding(12);
    cellFormat.setRightPadding(12);
    cell.setFormat(cellFormat);

    m_streamCursor = cell.firstCursorPosition();

    QTextCharFormat labelFormat;
    labelFormat.setForeground(QColor(QStringLiteral("#b9f6c8")));
    labelFormat.setFontWeight(QFont::DemiBold);
    labelFormat.setFontPointSize(9);
    m_streamCursor.insertText(QStringLiteral("Nexus"), labelFormat);
    m_streamCursor.insertBlock();

    // Keep body text visually consistent with the QTextBrowser's default
    // font while preserving the cursor's ability to insert plain streamed
    // text efficiently.
    QTextCharFormat bodyFormat;
    bodyFormat.setForeground(Qt::white);
    bodyFormat.setFontPointSize(13);
    m_streamCursor.setCharFormat(bodyFormat);

    m_streamBuffer.clear();
    m_activeStreamText.clear();
    m_isStreaming = true;

    // The indicator represents AI activity, not the window's visual state.
    m_indicator->setState(NexusIndicator::State::Thinking);

    if (!m_userScrolledUp)
        scrollToBottom();

    if (!m_heightUpdateTimer->isActive())
        m_heightUpdateTimer->start(kHeightUpdateMs);
}

void DynamicIslandWindow::flushStreamBuffer()
{
    if (m_streamBuffer.isEmpty())
        return;

    if (!m_isStreaming)
        createStreamingAssistantBubble();

    const QString chunk = std::exchange(m_streamBuffer, QString());
    m_activeStreamText += chunk;

    // Insert directly into the active body. No setHtml(), no rebuilding of
    // previous messages, and no Markdown parsing during generation.
    m_streamCursor.insertText(chunk);

    // Keep following the AI only while the user remains at the bottom.
    // Once they scroll upward, streamed tokens leave their viewport alone.
    if (!m_userScrolledUp)
        scrollToBottom();

    if (!m_heightUpdateTimer->isActive())
        m_heightUpdateTimer->start(kHeightUpdateMs);

    if (!m_streamBuffer.isEmpty() && !m_streamCoalesceTimer->isActive())
        m_streamCoalesceTimer->start(kStreamCoalesceMs);
}

void DynamicIslandWindow::finalizeStreamingResponse(const QString &fullText)
{
    m_streamCoalesceTimer->stop();
    flushStreamBuffer();

    // The backend's completed response is authoritative. Re-rendering once
    // here is cheap compared with rebuilding the whole document per token,
    // and it gives us proper Markdown formatting for the final answer.
    appendAssistantMessage(fullText);

    m_input->setEnabled(true);
    m_input->setFocus();
    m_statusLabel->setText(QStringLiteral("Nexus AI"));

    // Orange means the response has just completed while the panel is open.
    // If the user collapsed the island during generation, return to the
    // normal green idle indicator instead.
    if (m_state == State::Idle || m_state == State::Compact)
        m_indicator->setState(NexusIndicator::State::Idle);
    else
        m_indicator->setState(NexusIndicator::State::Active);
}

void DynamicIslandWindow::scrollToBottom()
{
    if (QScrollBar *bar = m_chatView->verticalScrollBar())
    {
        m_programmaticScroll = true;
        bar->setValue(bar->maximum());
        m_programmaticScroll = false;

        // Explicitly reaching the bottom resumes follow mode.
        m_userScrolledUp = false;
    }
}

void DynamicIslandWindow::updateExpandedHeight()
{
    if (m_state != State::Input && m_state != State::Expanded)
        return;

    const int contentWidth = kExpandedWidth -
                             m_layout->contentsMargins().left() -
                             m_layout->contentsMargins().right() -
                             2 * m_chatView->document()->documentMargin();

    m_chatView->document()->setTextWidth(contentWidth);
    const int contentHeight = static_cast<int>(m_chatView->document()->size().height());

    constexpr int kChrome = 96;
    const int targetHeight = qBound(kExpandedMinHeight,
                                    contentHeight + kChrome,
                                    kExpandedMaxHeight);

    QRect newGeo(0, 0, kExpandedWidth, targetHeight);
    if (screen())
    {
        const QRect avail = screen()->availableGeometry();
        newGeo.moveLeft(avail.center().x() - newGeo.width() / 2);
        newGeo.moveTop(avail.top() + kTopMargin);
    }

    if (newGeo == geometry())
        return;

    m_geometryAnim->stop();
    m_geometryAnim->setStartValue(geometry());
    m_geometryAnim->setEndValue(newGeo);
    m_geometryAnim->start();
}

void DynamicIslandWindow::handleServerState(const QString &state)
{
    if (state == QLatin1String("idle"))
    {
        if (m_state == State::Compact)
            setState(State::Idle);
        return;
    }

    if (state == QLatin1String("compact"))
    {
        setState(State::Compact);
        return;
    }

    if (state == QLatin1String("expanded"))
    {
        m_streamBuffer.clear();
        m_activeStreamText.clear();
        m_isStreaming = false;
        m_streamCursor = QTextCursor();
        m_input->setEnabled(false);
        setState(State::Expanded);
        // The assistant bubble is created lazily on the first token
        // (see flushStreamBuffer/handleToken) so that a checklist bubble,
        // if one arrives for this turn, ends up above it rather than after.
        return;
    }
}

void DynamicIslandWindow::handleToken(const QString &token)
{
    if (!m_isStreaming)
        createStreamingAssistantBubble();

    m_streamBuffer += token;

    if (!m_streamCoalesceTimer->isActive())
        m_streamCoalesceTimer->start(kStreamCoalesceMs);
}

void DynamicIslandWindow::handleResponseComplete(const QString &fullText)
{
    finalizeStreamingResponse(fullText);
}

void DynamicIslandWindow::handleChecklist(const QString &title,
                                          const QJsonArray &items)
{
    updateTaskProgress(title, items);
}

#ifdef Q_OS_WIN
void DynamicIslandWindow::enableWindowsAcrylic()
{
    HWND hwnd = reinterpret_cast<HWND>(winId());
    if (!hwnd)
        return;

    HMODULE user32 = LoadLibraryW(L"user32.dll");
    if (!user32)
        return;

    auto setWindowCompositionAttribute = reinterpret_cast<SetWindowCompositionAttributeFn>(
        GetProcAddress(user32, "SetWindowCompositionAttribute"));

    if (setWindowCompositionAttribute)
    {
        ACCENT_POLICY accent{};
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND;
        accent.AccentFlags = 0;
        accent.GradientColor = 0x99201818;

        WINDOWCOMPOSITIONATTRIBDATA data{};
        data.Attrib = WCA_ACCENT_POLICY;
        data.pvData = &accent;
        data.cbData = sizeof(accent);

        setWindowCompositionAttribute(hwnd, &data);
    }

    FreeLibrary(user32);

    DwmSetWindowAttribute(hwnd,
                          kDwmwaWindowCornerPreference,
                          &kDwmwcpRound,
                          sizeof(kDwmwcpRound));
}
#endif