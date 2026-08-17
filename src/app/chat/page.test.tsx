import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ChatPage from "./page";

const { router } = vi.hoisted(() => ({ router: { push: vi.fn() } }));

vi.mock("next/navigation", () => ({
  useRouter: () => router,
}));

describe("ChatPage", () => {
  beforeEach(() => {
    localStorage.clear();
    router.push.mockClear();
    localStorage.setItem(
      "chat_user",
      JSON.stringify({ first_name: "Hana", internal_id: "user-1" }),
    );
  });

  afterEach(() => {
    cleanup();
  });

  it("welcomes the saved user by name", async () => {
    render(<ChatPage />);

    await waitFor(() => {
      expect(screen.getByText(/Hana/)).toBeDefined();
    });
  });

  it("fills the message input from a suggested prompt", () => {
    render(<ChatPage />);

    fireEvent.click(screen.getByRole("button", { name: "ጭንቀት ይሰማኛል" }));

    const input = screen.getByPlaceholderText("እዚህ ይጻፉ...") as HTMLInputElement;
    expect(input.value).toBe("ጭንቀት ይሰማኛል");
  });

  it("clears the saved session and returns home on logout", () => {
    render(<ChatPage />);

    fireEvent.click(screen.getByRole("button", { name: "ውጣ" }));

    expect(localStorage.getItem("chat_user")).toBeNull();
    expect(router.push).toHaveBeenCalledWith("/");
  });
});
