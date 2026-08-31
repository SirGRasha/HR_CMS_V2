import {
  Form,
  Input,
  Select,
  Space,
  Switch,
} from "antd"
import type { FormInstance } from "antd"

import type {
  OrganizationUnit,
} from "../../types/organization"

interface PositionFormValues {
  code: string
  title: string
  organization_unit: number
  is_active: boolean
  description: string
}

interface PositionFormProps {
  form: FormInstance<PositionFormValues>
  units: OrganizationUnit[]
}

export default function PositionForm({
  form,
  units,
}: PositionFormProps) {
  return (
    <Form
      form={form}
      layout="vertical"
      style={{
        marginTop: 20,
      }}
    >
      <Space
        direction="vertical"
        size="middle"
        style={{
          width: "100%",
        }}
      >
        <Form.Item
          label="کد پست"
          name="code"
          rules={[
            {
              required: true,
              message:
                "کد پست را وارد کنید.",
            },
            {
              max: 50,
              message:
                "کد پست نمی‌تواند بیشتر از ۵۰ کاراکتر باشد.",
            },
          ]}
        >
          <Input
            placeholder="مثلاً P-001"
            maxLength={50}
          />
        </Form.Item>

        <Form.Item
          label="عنوان پست"
          name="title"
          rules={[
            {
              required: true,
              message:
                "عنوان پست را وارد کنید.",
            },
            {
              max: 150,
              message:
                "عنوان پست نمی‌تواند بیشتر از ۱۵۰ کاراکتر باشد.",
            },
          ]}
        >
          <Input
            placeholder="مثلاً مدیر منابع انسانی"
            maxLength={150}
          />
        </Form.Item>

        <Form.Item
          label="واحد سازمانی"
          name="organization_unit"
          rules={[
            {
              required: true,
              message:
                "واحد سازمانی را انتخاب کنید.",
            },
          ]}
        >
          <Select
            showSearch
            optionFilterProp="label"
            placeholder="واحد سازمانی را انتخاب کنید"
            options={units.map(
              (unit) => ({
                label: `${unit.code} - ${unit.name}`,
                value: unit.id,
              }),
            )}
          />
        </Form.Item>

        <Form.Item
          label="وضعیت"
          name="is_active"
          valuePropName="checked"
        >
          <Switch
            checkedChildren="فعال"
            unCheckedChildren="غیرفعال"
          />
        </Form.Item>

        <Form.Item
          label="توضیحات"
          name="description"
        >
          <Input.TextArea
            rows={4}
            placeholder="توضیحات مربوط به پست..."
            maxLength={1000}
            showCount
          />
        </Form.Item>
      </Space>
    </Form>
  )
}