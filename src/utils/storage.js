import { Preferences } from "@capacitor/preferences";

const storage = {
  /**
   * 保存数据到 Preferences，支持过期时间
   * @param {string} key 键
   * @param {any} value 值，可以是任意可序列化的数据
   * @param {number} expiryHours 过期时间，单位小时，默认24小时，如果为0则表示永不过期
   */
  set: async (key, value, expiryHours = 24) => {
    try {
      const data = {
        value: value,
        expiry: Date.now() + expiryHours * 60 * 60 * 1000,
        forever: expiryHours === 0,
      };
      await Preferences.set({
        key: key,
        value: JSON.stringify(data),
      });
    } catch (e) {
      console.error("存储失败:", e);
      throw new Error("无法序列化数据，保存失败");
    }
  },

  /**
   * 从 Preferences 获取数据，自动处理过期逻辑
   * @param {string} key
   * @returns {Promise<any|null>} 返回存储的数据，如果不存在或已过期则返回null
   */
  get: async (key) => {
    try {
      const { value } = await Preferences.get({ key });
      if (!value) {
        return null;
      }

      const data = JSON.parse(value);

      if (!data.forever && data.expiry && Date.now() > data.expiry) {
        await Preferences.remove({ key });
        return null;
      }

      return data.value;
    } catch (e) {
      console.error("数据读取或解析失败:", e);
      return null;
    }
  },

  /**
   * 删除数据
   * @param {string} key
   */
  remove: async (key) => {
    await Preferences.remove({ key });
  },

  /**
   * 清空所有存储
   */
  clear: async () => {
    await Preferences.clear();
  },
};

export default storage;
