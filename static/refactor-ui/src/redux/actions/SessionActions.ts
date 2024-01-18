import store from "..";
import { GET } from "../../utils/axios";
import {
  SET_SESSION_STATE,
  CLEAR_SESSION_STATE,
  SessionActionTypes,
} from "../types/SessionTypes";
import { Dispatch } from "redux";

export const setSessionState = (data: any) => {
  return (dispatch: Dispatch<SessionActionTypes>) => {
    dispatch({
      type: SET_SESSION_STATE,
      payload: data,
    });
  };
};

export const getSessionDataAction = (data: any): SessionActionTypes => {
  return {
    type: SET_SESSION_STATE,
    payload: data,
  };
};

export const clearSessionState = () => {
  return (dispatch: Dispatch<SessionActionTypes>) => {
    dispatch({
      type: CLEAR_SESSION_STATE,
      payload: {},
    });
  };
};

export const prepareSessionData = async () => {
  const res = await GET(`api/account/session`);
  store.dispatch(getSessionDataAction(res?.data));
  return res?.data;
};
