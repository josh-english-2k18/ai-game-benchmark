import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";

const renderWithProviders = () => {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  );
};

describe("App", () => {
  it("renders header text", () => {
    renderWithProviders();
    expect(screen.getByText(/Silicon Showdown/i)).toBeInTheDocument();
  });
});
