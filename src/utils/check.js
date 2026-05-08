import router from "@/router";

function resCheck(res) {
  if (!res.ok) {
    console.log(res.status);
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res.json();
}

function authCheck(res) {
  if (res.code === 401) {
    // use vue-router to login page
    router.push("/login");
  }
  return res;
}

export { resCheck, authCheck };
