#include "WebSocketClient.h"

#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>

WebSocketClient::WebSocketClient(QObject* parent)
    : QObject(parent) {
    connect(&m_socket, &QWebSocket::connected, this, &WebSocketClient::onConnected);
    connect(&m_socket, &QWebSocket::disconnected, this, &WebSocketClient::onDisconnected);
    connect(&m_socket, &QWebSocket::textMessageReceived, this, &WebSocketClient::onTextMessageReceived);
    connect(&m_socket, &QWebSocket::errorOccurred, this, &WebSocketClient::onErrorOccurred);
}

void WebSocketClient::connectToServer(const QUrl& url) {
    m_socket.open(url);
}

bool WebSocketClient::isConnected() const {
    return m_socket.state() == QAbstractSocket::ConnectedState;
}

void WebSocketClient::sendPrompt(const QString& text) {
    qDebug() << "sendPrompt called";
    qDebug() << "Connected:" << isConnected();
    if (!isConnected()) {
        qDebug() << "Not connected!";
        return;
    }
    qDebug() << "Sending:" << text;

    QJsonObject obj;
    obj["type"] = "prompt";
    obj["text"] = text;
    m_socket.sendTextMessage(QJsonDocument(obj).toJson(QJsonDocument::Compact));
}

void WebSocketClient::onConnected() {
    emit connected();
}

void WebSocketClient::onDisconnected() {
    emit disconnected();
}

void WebSocketClient::onTextMessageReceived(const QString& message) {
    qDebug() << "RAW MESSAGE:" << message;
    const QJsonDocument doc = QJsonDocument::fromJson(message.toUtf8());
    if (!doc.isObject())
        return;

    const QJsonObject obj = doc.object();
    const QString type = obj.value("type").toString();

    if (type == "state")
    {
        emit stateReceived(obj.value("value").toString());
    }
    else if (type == "token")
    {
        emit tokenReceived(obj.value("text").toString());
    }
    else if (type == "response")
    {
        emit responseComplete(obj.value("text").toString());
    }
    else if (type == "checklist")
    {
        emit checklistReceived(
            obj.value("title").toString(),
            obj.value("items").toArray()
        );
    }
    // Unknown message types are ignored rather than treated as errors, so
    // the protocol can grow (e.g. adding an "error" type later) without
    // breaking older clients.
}

void WebSocketClient::onErrorOccurred(QAbstractSocket::SocketError error) {
    Q_UNUSED(error);
    emit connectionError(m_socket.errorString());
}
