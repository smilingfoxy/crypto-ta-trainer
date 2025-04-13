# Add near the top after app initialization
server = app.server

# Replace the app entry point at the bottom
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=10000)