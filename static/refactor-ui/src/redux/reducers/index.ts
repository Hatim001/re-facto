import { combineReducers } from "redux";
import { SessionReducer } from "./SessionReducer";

export const rootReducer = combineReducers({
  session: SessionReducer,
});
