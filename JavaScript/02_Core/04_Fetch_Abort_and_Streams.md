---
tags: [javascript, core, fetch, abort, streams, signal, abort-controller, readable-stream, writable-stream, transform-stream, backpressure]
aliases: ["Fetch API", "AbortController", "Streams API", "AbortSignal", "ReadableStream", "WritableStream"]
status: stable
updated: 2026-05-11
---

# Fetch, Abort, and Streams

> [!summary] Goal
> Master the modern HTTP and stream APIs: `fetch()` for HTTP requests/responses, `AbortController`/`AbortSignal` for cancellation, the Streams API (`ReadableStream`, `WritableStream`, `TransformStream`) for streaming data processing, and integration between them.

## Table of Contents

1. [fetch() Deep Dive](#fetch-deep-dive)
2. [AbortController and AbortSignal](#abortcontroller-and-abortsignal)
3. [ReadableStream](#readablestream)
4. [WritableStream](#writablestream)
5. [TransformStream](#transformstream)
6. [Streams Integration](#streams-integration)

---

## `fetch()` Deep Dive

> [!info] fetch()
> `fetch()` is the modern replacement for `XMLHttpRequest`. It returns a `Promise<Response>` and supports streaming, request/response headers, and cancellation via `AbortSignal`. Since Node.js 18, it's also available server-side (behind `--experimental-fetch` flag, then stable in Node 21+).

```javascript
// Basic request
const response = await fetch('https://api.example.com/users');
const data = await response.json();
```

### Request and Response

```javascript
// Request object — controls every aspect of the request
const request = new Request('https://api.example.com/users', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer token123',
        'Accept': 'application/json',
    },
    body: JSON.stringify({ name: 'Alice' }),
    signal: AbortSignal.timeout(5000),  // 5 second timeout
    // Other options: cache, credentials, integrity, keepalive, mode, redirect, referrer
});

const response = await fetch(request);

// Response object:
console.log(response.status);       // 200
console.log(response.statusText);   // "OK"
console.log(response.ok);           // true (status 200-299)
console.log(response.headers.get('content-type'));  // "application/json"

// Body methods (can only call ONE):
const json = await response.json();        // Parse as JSON
const text = await response.text();        // Parse as text
const blob = await response.blob();        // Binary blob
const arrayBuffer = await response.arrayBuffer();  // Raw bytes
const stream = response.body;              // ReadableStream (for streaming)

// Clone response (if you need multiple reads):
const r1 = response.clone();
const r2 = response.clone();
```

### Streaming response body

```javascript
// Stream a large download without buffering everything in memory:

const response = await fetch('https://example.com/large-file.csv');
const reader = response.body.getReader();
const decoder = new TextDecoder();

let result = '';
while (true) {
    const { done, value } = await reader.read();  // Read chunks
    if (done) break;
    result += decoder.decode(value, { stream: true });
}
// Final decode for remaining bytes:
result += decoder.decode();

// Progress tracking:
const total = parseInt(response.headers.get('content-length') || '0');
let loaded = 0;

const progressReader = response.body.getReader();
while (true) {
    const { done, value } = await progressReader.read();
    if (done) break;
    loaded += value.length;
    console.log(`Progress: ${(loaded / total * 100).toFixed(1)}%`);
}
```

---

## AbortController and AbortSignal

> [!info] Abort API
> `AbortController` and `AbortSignal` provide a standard cancellation protocol used by `fetch()`, the Streams API, and custom async operations. `AbortSignal` is the "listener" side (passed to consumers), `AbortController` is the "trigger" side (used to cancel).

```javascript
// Basic abort pattern:
const controller = new AbortController();

// Pass signal to fetch:
fetch('https://api.example.com/slow-endpoint', {
    signal: controller.signal,
});

// Cancel the request elsewhere:
controller.abort();  // fetch throws AbortError
```

### `AbortSignal.timeout()`

```javascript
// Simplest timeout pattern — single static call:
const response = await fetch('https://api.example.com', {
    signal: AbortSignal.timeout(3000)  // Auto-abort after 3 seconds
});

// Equivalent to:
const controller = new AbortController();
setTimeout(() => controller.abort(), 3000);
fetch(url, { signal: controller.signal });
```

### `AbortSignal.any()` (ES2024)

```javascript
// Combine multiple signals — abort when ANY of the signals fires:
const timeoutSignal = AbortSignal.timeout(5000);
const userController = new AbortController();

// User clicks "cancel":
cancelButton.onclick = () => userController.abort();

const combined = AbortSignal.any([
    timeoutSignal,
    userController.signal,
]);

fetch('https://api.example.com', { signal: combined });
// Either timeout OR user cancel triggers the abort

// Checking abort reason:
try {
    await fetch(url, { signal: combined });
} catch (err) {
    if (err.name === 'AbortError') {
        console.log('Aborted because:', combined.reason);
    }
}
```

### Custom async operations with AbortSignal

```javascript
function waitWithCancel(ms, signal) {
    return new Promise((resolve, reject) => {
        const timer = setTimeout(resolve, ms);
        signal.addEventListener('abort', () => {
            clearTimeout(timer);
            reject(signal.reason || new DOMException('Aborted', 'AbortError'));
        }, { once: true });
    });
}

// Usage:
const controller = new AbortController();
const delayedTask = waitWithCancel(10000, controller.signal);
setTimeout(() => controller.abort(new Error('Cancelled by user')), 2000);
await delayedTask;  // Throws after 2 seconds
```

---

## ReadableStream

> [!info] ReadableStream
> `ReadableStream` represents a source of data that you can read chunk by chunk. It provides the `getReader()` method for reading, supports `cancel()` and `tee()` (split into two streams). Used for: file downloads, fetch response bodies, I/O streams.

```javascript
// Creating a readable stream:
const readable = new ReadableStream({
    start(controller) {
        controller.enqueue('chunk 1');
        controller.enqueue('chunk 2');
        controller.close();  // No more data
    },
});

// Reading with a reader:
const reader = readable.getReader();
const { value, done } = await reader.read();   // { value: 'chunk 1', done: false }

// Iterating all chunks:
const asyncIterable = {
    [Symbol.asyncIterator]() {
        return readable.getReader();
    }
};
for await (const chunk of asyncIterable) {
    console.log(chunk);
}

// Tee — split one stream into two (like Unix tee):
const [streamA, streamB] = readable.tee();
// Both streams receive the same data independently
```

### Canceling a stream

```javascript
const reader = readable.getReader();
// Cancel consuming:
await reader.cancel('no longer needed');
// The stream source receives the cancel reason
```

---

## WritableStream

> [!info] WritableStream
> `WritableStream` represents a destination for data, like a file or network socket. You write to it via `getWriter()`.

```javascript
const writable = new WritableStream({
    write(chunk) {
        // Process each chunk
        console.log('Writing:', chunk);
    },
    close() {
        console.log('Stream closed');
    },
    abort(reason) {
        console.log('Stream aborted:', reason);
    },
});

const writer = writable.getWriter();
await writer.write('data chunk 1');
await writer.write('data chunk 2');
await writer.close();
```

---

## TransformStream

> [!info] TransformStream
> `TransformStream` is a pair of a readable and writable stream that transforms data as it passes through. Chain transformations with `pipeThrough()`.

```javascript
// Built-in transform streams:
// TextEncoderStream — string → Uint8Array
// TextDecoderStream — Uint8Array → string
// CompressionStream — compress data (gzip, deflate)
// DecompressionStream — decompress data

// Custom transform stream:
const uppercaseStream = new TransformStream({
    transform(chunk, controller) {
        controller.enqueue(chunk.toUpperCase());
    },
});

// Usage:
const response = await fetch('https://example.com/data.txt');
const transformed = response.body
    .pipeThrough(new TextDecoderStream())     // bytes → text
    .pipeThrough(uppercaseStream)            // text → uppercase text
    .pipeThrough(new TextEncoderStream());   // text → bytes

// The transformed stream can be consumed chunk by chunk
```

### Piping streams

```javascript
// pipeThrough — connect through a transform:
const readableUpperCase = readable
    .pipeThrough(new TextDecoderStream())
    .pipeThrough(uppercaseTransform)
    .pipeThrough(new TextEncoderStream());

// pipeTo — pipe to a writable destination:
await readableUpperCase.pipeTo(writableStream);
// Returns a Promise that resolves when piping completes.

// AbortSignal integration:
await readable.pipeTo(writable, {
    signal: AbortSignal.timeout(5000),
    preventClose: false,    // Close destination when source ends?
    preventAbort: false,    // Abort destination on error?
    preventCancel: false,   // Cancel source on error?
});
```

---

## Streams Integration

### Fetch + Streams + Abort

```javascript
// Complete pattern: stream a large JSON API response with cancellation:

async function streamJSON(url, onChunk, signal) {
    const response = await fetch(url, { signal });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body
        .pipeThrough(new TextDecoderStream())
        .pipeThrough(parseJSONLines())  // Custom transform
        .getReader();

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            onChunk(value);
        }
    } finally {
        reader.cancel();
    }
}
```

### Custom TransformStream: parse JSON lines

```javascript
function parseJSONLines() {
    let buffer = '';
    return new TransformStream({
        transform(chunk, controller) {
            buffer += chunk;
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';  // Keep incomplete line

            for (const line of lines) {
                if (line.trim()) {
                    try {
                        controller.enqueue(JSON.parse(line));
                    } catch {
                        // Skip malformed lines
                    }
                }
            }
        },
        flush(controller) {
            if (buffer.trim()) {
                try { controller.enqueue(JSON.parse(buffer)); } catch {}
            }
        },
    });
}
```

---

## Cross-Links

- [[JavaScript/01_Foundations/04_Async_Promises_and_AsyncAwait]] for Promise fundamentals
- [[JavaScript/01_Foundations/05_ES2023_2024_Features_and_Symbol]] for AbortSignal.timeout, Promise.withResolvers
- [[JavaScript/02_Core/03_Performance_and_Memory]] for memory impact of buffered vs streaming reads
- [[JavaScript/03_Advanced/02_Event_Loop_Starvation_and_Backpressure]] for event loop and backpressure
