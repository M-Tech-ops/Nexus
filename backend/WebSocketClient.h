#pragma once

#include <QObject>
#include <QUrl>
#include <QtWebSockets/QWebSocket>

// Thin wrapper around QWebSocket that speaks the backend's JSON protocol:
//
// Client -> Server:
//   {"type": "prompt", "text": "..."}
//
// Server -> Client:
//   {"type": "state", "value": "idle" | "compact" | "expanded"}
//   {"type": "token", "text": "..."}     // one per streamed chunk
//   {"type": "response", "text": "..."}  // full text once streaming finishes
class WebSocketClient : public QObject
{
    Q_OBJECT

public:
    explicit WebSocketClient(QObject *parent = nullptr);

    void connectToServer(const QUrl &url);
    void sendPrompt(const QString &text);
    bool isConnected() const;

signals:
    void connected();
    void disconnected();
    void stateReceived(const QString &state);
    void tokenReceived(const QString &token);
    void responseComplete(const QString &fullText);
    void connectionError(const QString &errorString);

private slots:
    void onConnected();
    void onDisconnected();
    void onTextMessageReceived(const QString &message);
    void onErrorOccurred(QAbstractSocket::SocketError error);

private:
    QWebSocket m_socket;
};