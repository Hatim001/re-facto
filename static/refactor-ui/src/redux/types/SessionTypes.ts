export const SET_SESSION_STATE = "SET_SESSION_STATE";
export const CLEAR_SESSION_STATE = "CLEAR_SESSION_STATE";

interface SetSessionState {
  type: typeof SET_SESSION_STATE | typeof CLEAR_SESSION_STATE;
  payload: {};
}

export type SessionActionTypes = SetSessionState;
