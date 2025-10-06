type LogLevel = 'info' | 'warn' | 'error' | 'debug';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: any;
}

class Logger {
  private static instance: Logger;
  private readonly maxLogSize = 1000;
  private logs: LogEntry[] = [];
  private readonly isProd = import.meta.env.MODE === 'production';

  private constructor() {
    window.addEventListener('error', (event) => {
      this.error('Unhandled error:', {
        message: event.error?.message,
        stack: event.error?.stack,
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.error('Unhandled promise rejection:', {
        reason: event.reason,
      });
    });
  }

  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private formatMessage(level: LogLevel, message: string, data?: any): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      data,
    };
  }

  private store(entry: LogEntry) {
    this.logs.push(entry);
    if (this.logs.length > this.maxLogSize) {
      this.logs.shift();
    }

    // In development, also use console
    if (!this.isProd) {
      const consoleMethod = entry.level === 'error' ? 'error' :
        entry.level === 'warn' ? 'warn' :
        entry.level === 'debug' ? 'debug' : 'log';
      
      console[consoleMethod](
        `[${entry.timestamp}] [${entry.level.toUpperCase()}] ${entry.message}`,
        entry.data || ''
      );
    }

    // In production, you might want to send logs to a logging service
    if (this.isProd) {
      this.sendToLoggingService(entry);
    }
  }

  private async sendToLoggingService(entry: LogEntry) {
    // Implement your production logging service here
    // Example: Send to your logging endpoint
    try {
      await fetch('/api/logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entry),
      });
    } catch (error) {
      console.error('Failed to send log to logging service:', error);
    }
  }

  public debug(message: string, data?: any) {
    this.store(this.formatMessage('debug', message, data));
  }

  public info(message: string, data?: any) {
    this.store(this.formatMessage('info', message, data));
  }

  public warn(message: string, data?: any) {
    this.store(this.formatMessage('warn', message, data));
  }

  public error(message: string, data?: any) {
    this.store(this.formatMessage('error', message, data));
  }

  public getLogs(): LogEntry[] {
    return [...this.logs];
  }
}

export const logger = Logger.getInstance();