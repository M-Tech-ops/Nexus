#include <QApplication>
#include <QDebug>
#include <QUrl>

#include "DynamicislandWindow.h"
#include "backend/WebSocketClient.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    app.setQuitOnLastWindowClosed(true);

    DynamicIslandWindow island;
    WebSocketClient wsClient;

    // Backend -> frontend: server-driven state and streamed text.
    QObject::connect(&wsClient, &WebSocketClient::stateReceived,
                 &island, &DynamicIslandWindow::handleServerState);
    QObject::connect(&wsClient, &WebSocketClient::tokenReceived,
                     &island, &DynamicIslandWindow::handleToken);
    QObject::connect(&wsClient, &WebSocketClient::responseComplete,
                     &island, &DynamicIslandWindow::handleResponseComplete);
    QObject::connect(&wsClient, &WebSocketClient::checklistReceived,
                     &island, &DynamicIslandWindow::handleChecklist);

    // Frontend -> backend: user interaction requests a prompt.
    QObject::connect(&island, &DynamicIslandWindow::promptRequested,
                      &wsClient, &WebSocketClient::sendPrompt);

    QObject::connect(&wsClient, &WebSocketClient::connected, []()
                      { qDebug("Connected to Nexus AI backend."); });
    QObject::connect(&wsClient, &WebSocketClient::connectionError, [](const QString &err)
                      { qDebug("WebSocket error: %s", qPrintable(err)); });

    island.show();
    wsClient.connectToServer(QUrl("ws://127.0.0.1:8000/ws"));

    return app.exec();
}