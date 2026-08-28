import {
  Layout,
  Menu,
  Typography,
  Button,
  Space,
} from "antd"
import {
  DashboardOutlined,
  TeamOutlined,
  ApartmentOutlined,
  DollarOutlined,
  FileTextOutlined,
  FormOutlined,
  MailOutlined,
  BellOutlined,
  SafetyOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  LogoutOutlined,
} from "@ant-design/icons"
import {
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom"
import { useState } from "react"
import { logout } from "../../api/auth"

const {
  Header,
  Sider,
  Content,
} = Layout

const { Text } = Typography

const menuItems = [
  {
    key: "/dashboard",
    icon: <DashboardOutlined />,
    label: "داشبورد",
  },
  {
    key: "/employees",
    icon: <TeamOutlined />,
    label: "کارکنان",
  },
  {
    key: "/organization",
    icon: <ApartmentOutlined />,
    label: "ساختار سازمانی",
    disabled: true,
  },
  {
    key: "/payroll",
    icon: <DollarOutlined />,
    label: "حقوق و دستمزد",
    disabled: true,
  },
  {
    key: "/documents",
    icon: <FileTextOutlined />,
    label: "اسناد",
    disabled: true,
  },
  {
    key: "/requests",
    icon: <FormOutlined />,
    label: "درخواست‌ها",
    disabled: true,
  },
  {
    key: "/correspondence",
    icon: <MailOutlined />,
    label: "مکاتبات",
    disabled: true,
  },
  {
    key: "/notifications",
    icon: <BellOutlined />,
    label: "اعلان‌ها",
    disabled: true,
  },
  {
    key: "/audit",
    icon: <SafetyOutlined />,
    label: "حسابرسی",
    disabled: true,
  },
]

export default function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()

  const [collapsed, setCollapsed] =
    useState(false)

  const handleLogout = async () => {
    try {
      await logout()
    } finally {
      navigate("/login", {
        replace: true,
      })
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        direction: "rtl",
      }}
    >
      <Layout
        style={{
          minHeight: "100vh",
          direction: "rtl",
        }}
      >
        <Sider
          collapsible
          collapsed={collapsed}
          trigger={null}
          width={240}
          collapsedWidth={80}
          theme="dark"
          style={{
            position: "fixed",
            top: 0,
            right: 0,
            bottom: 0,
            zIndex: 100,
            overflow: "auto",
          }}
        >
          <div
            style={{
              height: 64,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderBottom:
                "1px solid rgba(255,255,255,0.1)",
              direction: "rtl",
            }}
          >
            <Text
              strong
              style={{
                color: "#fff",
                fontSize:
                  collapsed ? 16 : 20,
              }}
            >
              {collapsed
                ? "HR"
                : "HR_CG_V2"}
            </Text>
          </div>

          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[
              location.pathname,
            ]}
            items={menuItems}
            onClick={({ key }) => {
              navigate(key)
            }}
            style={{
              direction: "rtl",
            }}
          />
        </Sider>

        <Layout
          style={{
            marginRight:
              collapsed ? 80 : 240,
            minHeight: "100vh",
          }}
        >
          <Header
            style={{
              padding: "0 24px",
              background: "#fff",
              display: "flex",
              alignItems: "center",
              justifyContent:
                "space-between",
              direction: "rtl",
              borderBottom:
                "1px solid #f0f0f0",
            }}
          >
            <Space size="middle">
              <Button
                type="text"
                icon={
                  collapsed ? (
                    <MenuUnfoldOutlined />
                  ) : (
                    <MenuFoldOutlined />
                  )
                }
                onClick={() =>
                  setCollapsed(
                    !collapsed,
                  )
                }
              />

              <Text strong>
                سامانه مدیریت منابع انسانی
              </Text>
            </Space>

            <Space size="middle">
              <Text>
                reza
              </Text>

              <Button
                type="text"
                danger
                icon={
                  <LogoutOutlined />
                }
                onClick={
                  handleLogout
                }
              >
                خروج
              </Button>
            </Space>
          </Header>

          <Content
            style={{
              padding: 24,
              background: "#f5f5f5",
              direction: "rtl",
            }}
          >
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </div>
  )
}