function resCheck(res) {
  if (!res.ok) {
    console.log(res.status);
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res.json();
}

function authCheck(res) {
  if (res.code === 200) {
    return res;
  }
  // use browser native route to login page
  window.location.href = "/login";
}

export { resCheck, authCheck };
