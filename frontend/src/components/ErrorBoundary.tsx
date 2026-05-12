import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

/** Root-level error boundary. Renders a fallback with inline styles so it
 *  works even if the app's external CSS failed to load.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: "" };

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      message: error?.message ?? "Unknown error",
    };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // eslint-disable-next-line no-console
    console.error("[SkyCoach] root error boundary caught:", error, info);
  }

  handleReload = () => {
    if (typeof window !== "undefined") window.location.reload();
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "2rem",
          color: "#f5f3ff",
          fontFamily:
            "Plus Jakarta Sans, system-ui, -apple-system, Segoe UI, sans-serif",
          background:
            "linear-gradient(135deg, #1a0c2e 0%, #2a0a3a 50%, #0c0419 100%)",
        }}>
        <div
          style={{
            maxWidth: 540,
            width: "100%",
            padding: "2rem",
            borderRadius: 16,
            border: "1px solid rgba(187, 77, 251, 0.35)",
            background: "rgba(15, 7, 34, 0.85)",
            boxShadow: "0 24px 64px rgba(0, 0, 0, 0.6)",
          }}>
          <h1
            style={{
              margin: 0,
              marginBottom: "0.75rem",
              fontSize: "1.5rem",
            }}>
            Something went wrong loading SkyCoach AI
          </h1>
          <p style={{ margin: 0, marginBottom: "1rem", color: "#cbd5e1" }}>
            The app hit an unexpected error while starting. Hard-refresh
            usually fixes it. If it keeps happening, the backend may be
            unreachable - the app's task and theme features still work
            offline.
          </p>
          <pre
            style={{
              margin: 0,
              marginBottom: "1.5rem",
              padding: "0.75rem 1rem",
              borderRadius: 8,
              background: "rgba(0, 0, 0, 0.4)",
              color: "#fda4af",
              fontSize: "0.85rem",
              overflowX: "auto",
            }}>
            {this.state.message}
          </pre>
          <button
            type="button"
            onClick={this.handleReload}
            style={{
              padding: "0.6rem 1.2rem",
              borderRadius: 10,
              border: "none",
              cursor: "pointer",
              background:
                "linear-gradient(135deg, #bb4dfb 0%, #7c3aed 100%)",
              color: "white",
              fontWeight: 600,
            }}>
            Reload
          </button>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
