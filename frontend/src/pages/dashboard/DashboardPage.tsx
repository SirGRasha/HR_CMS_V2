import {
  Card,
  Typography,
} from "antd"

const { Title, Paragraph } = Typography

export default function DashboardPage() {
  return (
    <div className="dashboard-page">
      <Card>
        <Title level={2}>
          داشبورد
        </Title>

        <Paragraph>
          به سامانه مدیریت منابع انسانی
          HR_CG_V2 خوش آمدید.
        </Paragraph>
      </Card>
    </div>
  )
}