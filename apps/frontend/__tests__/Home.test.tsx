import { render, screen } from "@testing-library/react";
import HomePage from "@/app/page";

describe("HomePage", () => {
  it("renders Subscribers Enter and Admin Enter links", () => {
    render(<HomePage />);
    const sub = screen.getByRole("link", { name: /subscribers enter/i });
    const admin = screen.getByRole("link", { name: /admin enter/i });
    expect(sub).toHaveAttribute("href", "/subscribers");
    expect(admin).toHaveAttribute("href", "/admin");
  });
});
