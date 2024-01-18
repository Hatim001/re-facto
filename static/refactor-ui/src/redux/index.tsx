import thunkMiddleware from "redux-thunk";
import { configureStore } from "@reduxjs/toolkit";
import { rootReducer } from "./reducers";

const isProduction = process.env.REACT_APP_BUILD_ENV === "production";

const store = configureStore({
  reducer: rootReducer,
  devTools: !isProduction,
  middleware: (getDefaultMiddleware: any) =>
    getDefaultMiddleware({
      serializableCheck: false,
      immutableCheck: false,
    }).concat(thunkMiddleware),
});

export type AppState = ReturnType<typeof rootReducer>;
export default store;
