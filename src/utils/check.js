function resCheck(res) {
  if (!res.ok) {
    console.log(res.status);
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res.json();
}

function authCheck(res) {
  if (res.code === 401) {
    // use browser native route to login page
    window.location.href = "/login";
  }
  return res;
}

export { resCheck, authCheck };
