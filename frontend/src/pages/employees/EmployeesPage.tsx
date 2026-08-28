import {
  Alert,
  Button,
  Card,
  Input,
  Select,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
} from "antd"
import type { ColumnsType } from "antd/es/table"
import {
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
} from "@ant-design/icons"
import { useEffect, useMemo, useState } from "react"
import {
  getEmployees,
} from "../../api/employees"
import type {
  Employee,
} from "../../types/employee"

const { Title, Text } = Typography

export default function EmployeesPage() {
  const [employees, setEmployees] =
    useState<Employee[]>([])

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  const [search, setSearch] =
    useState("")

  const [activeFilter, setActiveFilter] =
    useState<boolean | undefined>(
      undefined,
    )

  const loadEmployees =
    async () => {
      try {
        setLoading(true)
        setError(null)

        const response =
          await getEmployees({
            is_active:
              activeFilter,
          })

        setEmployees(
          response.results,
        )
      } catch (err) {
        console.error(err)

        setError(
          "دریافت اطلاعات کارکنان با خطا مواجه شد.",
        )
      } finally {
        setLoading(false)
      }
    }

  useEffect(() => {
    loadEmployees()
  }, [activeFilter])

  const filteredEmployees =
    useMemo(() => {
      const query =
        search.trim().toLowerCase()

      if (!query) {
        return employees
      }

      return employees.filter(
        (employee) => {
          return [
            employee.personnel_code,
            employee.first_name,
            employee.last_name,
            employee.national_id,
            employee.job_title,
            employee.department,
          ]
            .filter(Boolean)
            .some((value) =>
              String(value)
                .toLowerCase()
                .includes(query),
            )
        },
      )
    }, [employees, search])

  const columns: ColumnsType<Employee> =
    [
      {
        title: "ردیف",
        key: "index",
        width: 70,
        render: (
          _,
          __,
          index,
        ) => index + 1,
      },

      {
        title: "کد پرسنلی",
        dataIndex:
          "personnel_code",
        key: "personnel_code",
      },

      {
        title: "نام و نام خانوادگی",
        key: "full_name",
        render: (_, record) =>
          `${record.first_name} ${record.last_name}`,
      },

      {
        title: "کد ملی",
        dataIndex:
          "national_id",
        key: "national_id",
      },

      {
        title: "سمت",
        key: "position",
        render: (_, record) =>
          record.position_detail
            ?.title ??
          record.job_title ??
          "—",
      },

      {
        title: "واحد سازمانی",
        key: "organization_unit",
        render: (_, record) =>
          record.position_detail
            ?.organization_unit
            ?.name ??
          record.department ??
          "—",
      },

      {
        title: "گروه پرسنلی",
        dataIndex:
          "employee_group",
        key: "employee_group",
      },

      {
        title: "وضعیت",
        dataIndex: "is_active",
        key: "is_active",
        render: (
          isActive: boolean,
        ) =>
          isActive ? (
            <Tag color="green">
              فعال
            </Tag>
          ) : (
            <Tag color="red">
              غیرفعال
            </Tag>
          ),
      },
    ]

  return (
    <div
      style={{
        direction: "rtl",
      }}
    >
      <Card>
        <Space
          direction="vertical"
          size="large"
          style={{
            width: "100%",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent:
                "space-between",
              gap: 16,
              flexWrap: "wrap",
            }}
          >
            <div>
              <Title
                level={2}
                style={{
                  margin: 0,
                }}
              >
                کارکنان
              </Title>

              <Text type="secondary">
                مدیریت اطلاعات کارکنان
              </Text>
            </div>

            <Button
              type="primary"
              icon={
                <PlusOutlined />
              }
            >
              افزودن کارمند
            </Button>
          </div>

          <Space
            wrap
            style={{
              width: "100%",
            }}
          >
            <Input
              allowClear
              prefix={
                <SearchOutlined />
              }
              placeholder="جستجو در کارکنان..."
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value,
                )
              }
              style={{
                width: 300,
              }}
            />

            <Select
              allowClear
              placeholder="وضعیت"
              style={{
                width: 160,
              }}
              value={activeFilter}
              onChange={(value) =>
                setActiveFilter(
                  value,
                )
              }
              options={[
                {
                  label: "همه",
                  value: undefined,
                },
                {
                  label: "فعال",
                  value: true,
                },
                {
                  label: "غیرفعال",
                  value: false,
                },
              ]}
            />

            <Button
              icon={
                <ReloadOutlined />
              }
              onClick={
                loadEmployees
              }
            >
              بروزرسانی
            </Button>
          </Space>

          {error && (
            <Alert
              type="error"
              showIcon
              message={error}
              action={
                <Button
                  size="small"
                  onClick={
                    loadEmployees
                  }
                >
                  تلاش مجدد
                </Button>
              }
            />
          )}

          {loading ? (
            <div
              style={{
                minHeight: 300,
                display: "flex",
                alignItems:
                  "center",
                justifyContent:
                  "center",
              }}
            >
              <Spin size="large" />
            </div>
          ) : (
            <Table<Employee>
              rowKey="id"
              columns={columns}
              dataSource={
                filteredEmployees
              }
              scroll={{
                x: 1100,
              }}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (
                  total,
                ) =>
                  `تعداد ${total} کارمند`,
              }}
              locale={{
                emptyText:
                  "کارمندی یافت نشد",
              }}
            />
          )}
        </Space>
      </Card>
    </div>
  )
}