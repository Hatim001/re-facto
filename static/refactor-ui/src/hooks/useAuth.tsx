import { createContext, useContext } from "react";

import { useLocalStorage } from "./useLocalStorage";
import { prepareSessionData, setSessionState } from "../redux/actions/SessionActions";
import { useDispatch } from "react-redux";
import { Dispatch } from "@reduxjs/toolkit";

const AuthContext = createContext<any>(null);

export const useAuth = () => {
  const [session, setSession] = useLocalStorage("session", null);
  const dispatch: Dispatch<any> = useDispatch();

  return {
    session: session,
    login(data: any) {
      return new Promise((res: any) => {
        setSession(data);
        prepareSessionData()
        res(data);
      });
    },
    logout() {
      return new Promise((res: any) => {
        setSession(null);
        dispatch(setSessionState(null))
        res();
      });
    },
  };
};

export const AuthProvider = ({ children }: any) => {
  const auth = useAuth();

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
};

export const AuthConsumer = () => {
  return useContext(AuthContext);
};
