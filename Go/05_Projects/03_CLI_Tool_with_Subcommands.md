---
tags: [go, projects, cli, cobra, command-line, tool]
aliases: ["CLI Tool Project", "Go Command Line", "Cobra CLI"]
status: stable
updated: 2026-05-03
---

# Project: CLI Tool with Subcommands

> [!summary] Goal
> Build a CLI tool with `cobra` supporting subcommands, flag parsing, config file loading, and structured output (JSON, table, text).

## Project Structure

```
mycli/
├── cmd/
│   ├── root.go
│   ├── serve.go
│   └── version.go
├── internal/
│   └── output/output.go
├── main.go
├── go.mod
└── Makefile
```

## main.go

```go
package main

import "mycli/cmd"

func main() {
    cmd.Execute()
}
```

## cmd/root.go

```go
package cmd

import (
    "fmt"
    "os"
    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var cfgFile string
var outputFormat string

var rootCmd = &cobra.Command{
    Use:   "mycli",
    Short: "mycli is a sample CLI tool",
    PersistentPreRun: func(cmd *cobra.Command, args []string) {
        initConfig()
    },
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}

func init() {
    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file")
    rootCmd.PersistentFlags().StringVarP(&outputFormat, "output", "o", "table", "output format: json, table, text")
    viper.BindPFlag("output", rootCmd.PersistentFlags().Lookup("output"))
}

func initConfig() {
    if cfgFile != "" {
        viper.SetConfigFile(cfgFile)
    } else {
        viper.AddConfigPath(".")
        viper.SetConfigName(".mycli")
    }
    viper.AutomaticEnv()
    viper.ReadInConfig()
}
```

## cmd/serve.go

```go
package cmd

import (
    "fmt"
    "github.com/spf13/cobra"
)

var serveCmd = &cobra.Command{
    Use:   "serve",
    Short: "Start the server",
    RunE: func(cmd *cobra.Command, args []string) error {
        port, _ := cmd.Flags().GetInt("port")
        fmt.Printf("starting server on port %d\n", port)
        return nil
    },
}

func init() {
    serveCmd.Flags().IntP("port", "p", 8080, "server port")
    rootCmd.AddCommand(serveCmd)
}
```

## cmd/version.go

```go
package cmd

import (
    "fmt"
    "mycli/internal/output"
    "github.com/spf13/cobra"
)

var version = "1.0.0"

var versionCmd = &cobra.Command{
    Use:   "version",
    Short: "Print version",
    RunE: func(cmd *cobra.Command, args []string) error {
        data := map[string]interface{}{
            "version":   version,
            "go_version": "1.22",
        }
        return output.Print(data, outputFormat)
    },
}

func init() {
    rootCmd.AddCommand(versionCmd)
}
```

## internal/output/output.go

```go
package output

import (
    "encoding/json"
    "fmt"
    "os"
    "text/tabwriter"
    "text/template"
)

func Print(data map[string]interface{}, format string) error {
    switch format {
    case "json":
        enc := json.NewEncoder(os.Stdout)
        enc.SetIndent("", "  ")
        return enc.Encode(data)
    case "table":
        w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
        for k, v := range data {
            fmt.Fprintf(w, "%s\t%v\n", k, v)
        }
        return w.Flush()
    case "text":
        tpl := template.Must(template.New("output").Parse(
            "{{range $k, $v := .}}{{$k}}: {{$v}}\n{{end}}"))
        return tpl.Execute(os.Stdout, data)
    default:
        return fmt.Errorf("unknown format: %s", format)
    }
}
```

## Makefile

```makefile
.PHONY: build test

build:
	go build -o mycli .

test:
	go test ./...

install:
	go install ./...
```

---

## Cross-Links

- [[Go/02_Core/07_Standard_Library_Reference]] for flag and sort reference
- [[Go/01_Foundations/06_Project_Layout_and_Design_Patterns]] for project structure
- [[Go/01_Foundations/05_Testing_Benchmarks_and_Profiling]] for CLI testing with golden files
