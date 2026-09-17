import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiClientError, request } from "./api";

function mockFetch(body: unknown, ok = true) {
  const raw = JSON.stringify(body);
  return vi.fn().mockResolvedValue({
    ok,
    status: ok ? 200 : 500,
    text: async () => raw,
    json: async () => body,
  });
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("request envelope handling", () => {
  it("unwraps the data field on success", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch({
        ok: true,
        data: { status: "ok", version: "2.0.0" },
        error: null,
        meta: { requestId: "r1", version: "2.0.0" },
      }),
    );
    const data = await request<{ status: string }>("/health");
    expect(data.status).toBe("ok");
  });

  it("throws ApiClientError with the mapped code on failure", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch({
        ok: false,
        data: null,
        error: { code: "NOT_FOUND", message: "Portfolio 'x' not found" },
        meta: { requestId: "r2", version: "2.0.0" },
      }),
    );
    await expect(request("/portfolios/x")).rejects.toMatchObject({
      code: "NOT_FOUND",
      message: "Portfolio 'x' not found",
    });
  });

  it("maps empty responses to a clear NETWORK_ERROR", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 502,
        text: async () => "",
        json: async () => {
          throw new Error("no json");
        },
      }),
    );
    const err = (await request("/health").catch((e) => e)) as ApiClientError;
    expect(err.code).toBe("NETWORK_ERROR");
    expect(err.message).toMatch(/make dev/);
  });

  it("maps transport failures to NETWORK_ERROR", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    const err = (await request("/health").catch((e) => e)) as ApiClientError;
    expect(err).toBeInstanceOf(ApiClientError);
    expect(err.code).toBe("NETWORK_ERROR");
  });
});
