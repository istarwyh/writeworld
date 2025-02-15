import type { ThemeConfig } from 'antd';

const themeConfig: ThemeConfig = {
  token: {
    // 主色调：水墨风
    colorPrimary: '#363945',     // 墨色
    colorInfo: '#363945',        // 信息色同主色
    colorSuccess: '#52c41a',     // 成功色保持清新
    colorWarning: '#E6B422',     // 金色作为警告色
    colorError: '#f5222d',       // 错误色保持醒目

    // 中性色
    colorTextBase: '#333333',    // 主文本色
    colorBgBase: '#FAFAFA',      // 背景基色（宣纸色）

    // 派生变量
    colorBgContainer: '#FFFFFF', // 容器背景色
    colorBorder: '#8B9DAF',     // 边框色（淡墨色）

    // 圆角
    borderRadius: 4,            // 基础圆角
    borderRadiusLG: 8,         // 大圆角

    // 字体
    fontFamily: "'Noto Serif SC', 'Crimson Pro', serif",
    fontSize: 16,              // 基础字号

    // 间距
    margin: 16,               // 基础外边距
    padding: 16,              // 基础内边距

    // 动画
    motion: true,             // 启用动画
    wireframe: false,         // 禁用线框风格
  },
  components: {
    Button: {
      primaryColor: '#363945',
      borderRadius: 4,
      controlHeight: 40,
    },
    Input: {
      controlHeight: 40,
      borderRadius: 4,
      paddingInline: 16,
    },
    Select: {
      controlHeight: 40,
      borderRadius: 4,
    },
    Card: {
      borderRadius: 8,
    },
  },
};

export default themeConfig;
