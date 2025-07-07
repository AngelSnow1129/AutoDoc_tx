package main

import (
	"fmt"
	"log"
	"net/http"
)

func main() {
	// 创建一个简单的 HTTP 处理器
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "<h1>Hello from Go Backend!</h1>")
		fmt.Fprintln(w, "<p>Your full-stack application is running.</p>")
	})

	port := "8080"
	fmt.Printf("Go server starting on http://localhost:%s\n", port)
	
	// 启动 HTTP 服务器
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Failed to start server: %s\n", err)
	}
}
