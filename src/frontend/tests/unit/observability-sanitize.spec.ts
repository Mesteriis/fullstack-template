import { sanitizeUrl } from "@/shared/observability/sanitize";

describe("observability sanitization", () => {
  it("removes query strings and masks identifier-like path segments", () => {
    expect(
      sanitizeUrl("https://api.example.test/widgets/12345678/details?token=secret"),
    ).toBe("https://api.example.test/widgets/:id/details");

    expect(
      sanitizeUrl("https://api.example.test/widgets/550e8400-e29b-41d4-a716-446655440000"),
    ).toBe("https://api.example.test/widgets/:id");
  });
});
