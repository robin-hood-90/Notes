---
tags: [javascript, node, eventemitter, buffer, child-process, cluster, advanced, fs]
aliases: ["Node.js", "EventEmitter", "Buffer", "child_process", "cluster", "path", "os", "fs deep"]
status: stable
updated: 2026-05-11
---

# Node.js: `EventEmitter`, `Buffer`, and System APIs

> [!summary] Goal
> Master Node.js core APIs: `EventEmitter` (pattern and deep usage), `Buffer` (binary data), `child_process` and `cluster` for multi-processing, and `path`/`os`/`fs` for system interactions.

## Table of Contents

1. [EventEmitter Deep Dive](#eventemitter-deep-dive)
2. [Buffer](#buffer)
3. [child_process](#childprocess)
4. [cluster](#cluster)
5. [path and os](#path-and-os)

---

## `EventEmitter` Deep Dive

> [!info] EventEmitter
> `EventEmitter` is the foundation of Node.js's event-driven architecture. Streams, servers, request/response, and many other modules inherit from it. Understanding EventEmitter is essential for mastering Node.js.

### Core API

```javascript
const EventEmitter = require('events');

const emitter = new EventEmitter();

// Register listeners:
emitter.on('data', handler);                     // Add listener
emitter.once('data', handler);                   // Fire once then remove
emitter.prependListener('data', handler);         // Add to front
emitter.prependOnceListener('data', handler);     // Once at front

// Emit events:
emitter.emit('data', payload);                    // Returns true if listeners existed
emitter.emit('error', new Error('oops'));         // Special: throws if no listener

// Remove listeners:
emitter.off('data', handler);                    // Remove specific
emitter.removeAllListeners('data');               // Remove all for event

// Inspect:
emitter.listeners('data');                        // Array of listener functions
emitter.rawListeners('data');                     // Includes wrapped ones (once)
emitter.listenerCount('data');                    // Number of listeners
emitter.eventNames();                              // Array of registered event names
```

### Error handling and captureRejections

```javascript
// The 'error' event is SPECIAL:
// If emitted with no listener, it THROWS (crashes the process).

// Always listen for error:
emitter.on('error', (err) => {
    console.error('Error:', err);
});

// Async event handling (Node.js 16+):
class AsyncEmitter extends EventEmitter {
    constructor() {
        super({ captureRejections: true });
        // When true, promise rejections from async handlers are
        // caught and emitted as 'error' instead of crashing.
    }
}

const ae = new AsyncEmitter();
ae.on('data', async (payload) => {
    throw new Error('async error');  // Caught by captureRejections → 'error' event
});
ae.on('error', (err) => console.log('Caught:', err.message));
ae.emit('data', {});
```

### Inheritance pattern

```javascript
// Most Node.js modules inherit EventEmitter via class:

class MyService extends EventEmitter {
    constructor() {
        super();
    }

    async start() {
        this.emit('start');
        try {
            const data = await this.fetchData();
            this.emit('data', data);
        } catch (err) {
            this.emit('error', err);
        }
    }

    async fetchData() { /* ... */ }
}

const service = new MyService();
service.on('data', (data) => console.log(data));
service.on('error', (err) => console.error(err));
service.start();
```

### Max listeners warning

```javascript
// If > 10 listeners are added to the same event, EventEmitter prints a warning.
// Useful for catching memory leaks.

emitter.setMaxListeners(20);  // Per-instance
EventEmitter.defaultMaxListeners = 50;  // Global (not recommended — use per-instance)

// Why this exists: if you add 100 listeners for 'data' and never remove them,
// you likely have a listener leak. Each listener keeps a reference to the callback,
// preventing GC.
```

---

## `Buffer`

> [!info] Buffer
> `Buffer` (Node.js-specific, not in browsers) provides raw binary data allocation and manipulation. It's used for file I/O, network protocols, encryption, and anything involving byte-level data.

```javascript
// Creating buffers:
const buf1 = Buffer.alloc(10);              // Zero-filled, 10 bytes
const buf2 = Buffer.alloc(10, 0xFF);         // Filled with 0xFF
const buf3 = Buffer.allocUnsafe(10);         // Uninitialized (faster, may contain old data)
const buf4 = Buffer.from('hello');           // From UTF-8 string
const buf5 = Buffer.from('hello', 'hex');    // From hex string
const buf6 = Buffer.from([0x48, 0x65, 0x6c]);// From byte array

// Reading/writing:
buf1.write('hello');                         // Write string
buf1.writeUInt8(0xFF, 0);                    // Write byte at offset
buf1.writeUInt16BE(0x1234, 2);               // Write 16-bit big-endian at offset 2
const val = buf1.readUInt32LE(4);            // Read 32-bit little-endian

// Encoding:
const str = buf1.toString('base64');         // "aGVsbG8="
const hex = buf1.toString('hex');            // "68656c6c6f"
const utf8 = buf1.toString('utf-8');         // "hello"

// Slicing (no copy — shares memory):
const slice = buf1.subarray(0, 5);           // First 5 bytes
slice[0] = 0x48;                             // Also modifies buf1!

// Copying:
const copy = Buffer.alloc(5);
buf1.copy(copy, 0, 0, 5);                   // Independent copy
copy[0] = 0x00;                              // Does NOT affect buf1

// Comparison:
const a = Buffer.from('abc');
const b = Buffer.from('abc');
console.log(Buffer.compare(a, b));           // 0 (equal)
console.log(a.equals(b));                    // true
console.log(a.indexOf('bc'));               // 1

// Concatenation:
const combined = Buffer.concat([buf1, buf2]);
```

---

## `child_process`

> [!info] child_process
> `child_process` spawns new OS processes from Node.js. Use `spawn` for streaming I/O, `exec` for capturing output, `execFile` for executables, and `fork` for Node.js modules.

```javascript
const { spawn, exec, execFile, fork } = require('child_process');

// spawn — streaming I/O (preferred for long-running processes)
const child = spawn('ls', ['-la', '/tmp'], {
    stdio: 'inherit',   // Share stdout/stderr with parent
    cwd: '/tmp',        // Working directory
    env: { ...process.env, MY_VAR: 'value' },  // Environment variables
});

child.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
});

child.on('exit', (code, signal) => {
    console.log(`Exited with code ${code}, signal ${signal}`);
});

child.on('error', (err) => {
    console.error('Failed to start:', err);
});

// exec — buffers output (for short-lived commands)
exec('ls -la', { maxBuffer: 1024 * 1024 }, (err, stdout, stderr) => {
    if (err) {
        console.error(`Error: ${err.message}`);
        return;
    }
    console.log(`stdout: ${stdout}`);
});

// execFile — like exec but without shell (safer)
execFile('/bin/ls', ['-la'], (err, stdout) => { /* ... */ });

// fork — spawn a Node.js script as a child process with IPC
const worker = fork('./worker.js');
worker.send({ task: 'process' });
worker.on('message', (msg) => console.log('Result:', msg));
```

---

## `cluster`

> [!info] cluster
> `cluster` allows a Node.js application to fork multiple worker processes on multi-core systems. The primary process distributes incoming connections among workers. This enables horizontal scaling within a single machine.

```javascript
const cluster = require('cluster');
const http = require('http');
const numCPUs = require('os').cpus().length;

if (cluster.isPrimary) {
    console.log(`Primary ${process.pid} is running`);

    // Fork workers
    for (let i = 0; i < numCPUs; i++) {
        cluster.fork();
    }

    // Handle worker crashes
    cluster.on('exit', (worker, code, signal) => {
        console.log(`Worker ${worker.process.pid} died`);
        cluster.fork();  // Replace the worker
    });

    // Graceful shutdown
    process.on('SIGTERM', () => {
        for (const id of Object.keys(cluster.workers)) {
            cluster.workers[id].kill();  // Send SIGTERM to each worker
        }
    });

} else {
    // Workers share the TCP connection
    const server = http.createServer((req, res) => {
        res.writeHead(200);
        res.end('Hello world\n');
    });

    server.listen(8000);
    console.log(`Worker ${process.pid} started`);
    // Round-robin scheduling (default on most platforms)
}

// For zero-downtime restarts:
// cluster.on('listening', (worker) => { /* signal ready */ });
```

---

## `path` and `os`

### `path` module

```javascript
const path = require('path');

const filePath = '/home/user/docs/file.txt';

console.log(path.dirname(filePath));      // '/home/user/docs'
console.log(path.basename(filePath));     // 'file.txt'
console.log(path.extname(filePath));      // '.txt'
console.log(path.parse(filePath));
// { root: '/', dir: '/home/user/docs', base: 'file.txt', ext: '.txt', name: 'file' }

console.log(path.join('/home', 'user', 'docs'));  // '/home/user/docs'
console.log(path.resolve('docs', 'file.txt'));     // '/current/working/dir/docs/file.txt'
console.log(path.relative('/home/user', '/home/user/docs/file.txt'));  // 'docs/file.txt'
console.log(path.isAbsolute('/home'));    // true
console.log(path.isAbsolute('relative')); // false
console.log(path.sep);                    // '/' on POSIX, '\\' on Windows
console.log(path.delimiter);              // ':' on POSIX, ';' on Windows

// Normalize path (resolve .. and .):
console.log(path.normalize('/home/../home/user/docs'));  // '/home/user/docs'
```

### `os` module

```javascript
const os = require('os');

console.log(os.cpus().length);              // Number of CPU cores
console.log(os.hostname());                  // Hostname
console.log(os.platform());                  // 'linux', 'darwin', 'win32'
console.log(os.type());                      // 'Linux', 'Darwin', 'Windows_NT'
console.log(os.release());                   // Kernel version
console.log(os.totalmem());                  // Total RAM in bytes
console.log(os.freemem());                   // Free RAM in bytes
console.log(os.uptime());                    // System uptime in seconds
console.log(os.networkInterfaces());         // Network interfaces
console.log(os.homedir());                   // Home directory
console.log(os.tmpdir());                    // Temp directory
console.log(os.userInfo());                  // Current user info
console.log(os.EOL);                         // '\n' on POSIX, '\r\n' on Windows
```

---

## Cross-Links

- [[JavaScript/01_Foundations/01_JS_Runtime_and_Event_Loop]] for the event loop
- [[JavaScript/02_Core/04_Fetch_Abort_and_Streams]] for streams integration
- [[JavaScript/03_Advanced/03_Node_Event_Loop_and_Libuv_Basics]] for libuv and Node event loop phases
- [[JavaScript/04_Playbooks/02_Profile_Node_CPU_and_Memory]] for profiling
