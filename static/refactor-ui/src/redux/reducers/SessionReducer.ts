import {
  CLEAR_SESSION_STATE,
  SET_SESSION_STATE,
  SessionActionTypes,
} from "../types/SessionTypes";

export const SessionReducer = (state = {}, action: SessionActionTypes) => {
  switch (action.type) {
    case SET_SESSION_STATE:
      return { ...state, ...action.payload };
    case CLEAR_SESSION_STATE:
      return {};
    default:
      return state;
  }
};
