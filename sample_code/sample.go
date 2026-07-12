package main

import (
	"fmt"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
    // security vulnerability: cross-site scripting (XSS)
	name := r.URL.Query().Get("name")
	fmt.Fprintf(w, "<html><body>Hello, %s</body></html>", name)
}

func main() {
	http.HandleFunc("/", handler)
	http.ListenAndServe(":8080", nil)
}
