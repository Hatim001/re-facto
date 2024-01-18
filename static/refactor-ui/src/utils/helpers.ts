import store from "../redux";

const prepareQueryParamsFromObject = (params: any) => {
  return new URLSearchParams(params || {})?.toString();
};

const getReduxState = (stateName: string) => {
  const state: any = store.getState();
  return state[stateName];
};

export { prepareQueryParamsFromObject, getReduxState };
