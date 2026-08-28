import {
  Button,
  Card,
  Form,
  Input,
  Typography,
  message,
} from "antd"
import { LockOutlined, UserOutlined } from "@ant-design/icons"
import { useNavigate } from "react-router-dom"
import { login } from "../../api/auth"

const { Title, Text } = Typography

interface LoginFormValues {
  username: string
  password: string
}

export default function LoginPage() {
  const navigate = useNavigate()

  const [messageApi, contextHolder] =
    message.useMessage()

  const handleSubmit = async (
    values: LoginFormValues,
  ) => {
    try {
      await login(values)

      messageApi.success(
        "ورود با موفقیت انجام شد",
      )

      navigate(
        "/dashboard",
        { replace: true },
      )
    } catch (error) {
      console.error(error)

      messageApi.error(
        "نام کاربری یا رمز عبور صحیح نیست",
      )
    }
  }

  return (
    <>
      {contextHolder}

      <div className="login-page">
        <Card
          className="login-card"
          bordered={false}
        >
          <div className="login-header">
            <Title level={2}>
              سامانه مدیریت منابع انسانی
            </Title>

            <Text type="secondary">
              HR_CG_V2
            </Text>
          </div>

          <Form
            layout="vertical"
            onFinish={handleSubmit}
            autoComplete="off"
          >
            <Form.Item
              label="نام کاربری"
              name="username"
              rules={[
                {
                  required: true,
                  message:
                    "نام کاربری را وارد کنید",
                },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="نام کاربری"
                size="large"
              />
            </Form.Item>

            <Form.Item
              label="رمز عبور"
              name="password"
              rules={[
                {
                  required: true,
                  message:
                    "رمز عبور را وارد کنید",
                },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="رمز عبور"
                size="large"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                block
                size="large"
              >
                ورود
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </div>
    </>
  )
}