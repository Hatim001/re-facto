import { Provider } from "react-redux";
import ReactDOM from "react-dom/client";
import { StyledEngineProvider } from "@mui/joy";
import { BrowserRouter } from "react-router-dom";

import "./global.css";
import App from "./App";
import store from "./redux";
import { AuthProvider } from "./hooks/useAuth";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);
root.render(
  <StyledEngineProvider injectFirst>
    <Provider store={store}>
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </Provider>
  </StyledEngineProvider>
);
