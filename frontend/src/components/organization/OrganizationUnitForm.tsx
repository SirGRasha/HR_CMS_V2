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
  OrganizationUnitType,
} from "../../types/organization"

interface OrganizationUnitFormValues {
  code: string
  name: string
  unit_type: OrganizationUnitType
  parent: number | null
  is_active: boolean
  description: string
}

interface OrganizationUnitFormProps {
  form: FormInstance<OrganizationUnitFormValues>
  units: OrganizationUnit[]
  editingUnit: OrganizationUnit | null
}

const unitTypeOptions = [
  {
    label: "شرکت",
    value: "company",
  },
  {
    label: "مدیریت",
    value: "management",
  },
  {
    label: "معاونت",
    value: "deputy",
  },
  {
    label: "دپارتمان",
    value: "department",
  },
  {
    label: "واحد",
    value: "unit",
  },
  {
    label: "بخش",
    value: "section",
  },
]

export default function OrganizationUnitForm({
  form,
  units,
  editingUnit,
}: OrganizationUnitFormProps) {
  const unitParentOptions = units
    .filter(
      (unit) =>
        unit.id !== editingUnit?.id,
    )
    .map((unit) => ({
      label: `${unit.code} - ${unit.name}`,
      value: unit.id,
    }))

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
          label="کد واحد"
          name="code"
          rules={[
            {
              required: true,
              message:
                "کد واحد را وارد کنید.",
            },
            {
              max: 50,
              message:
                "کد واحد نمی‌تواند بیشتر از ۵۰ کاراکتر باشد.",
            },
          ]}
        >
          <Input
            placeholder="مثلاً U-001"
            maxLength={50}
          />
        </Form.Item>

        <Form.Item
          label="نام واحد"
          name="name"
          rules={[
            {
              required: true,
              message:
                "نام واحد را وارد کنید.",
            },
            {
              max: 150,
              message:
                "نام واحد نمی‌تواند بیشتر از ۱۵۰ کاراکتر باشد.",
            },
          ]}
        >
          <Input
            placeholder="نام واحد سازمانی"
            maxLength={150}
          />
        </Form.Item>

        <Form.Item
          label="نوع واحد"
          name="unit_type"
          rules={[
            {
              required: true,
              message:
                "نوع واحد را انتخاب کنید.",
            },
          ]}
        >
          <Select
            placeholder="نوع واحد را انتخاب کنید"
            options={unitTypeOptions}
          />
        </Form.Item>

        <Form.Item
          label="واحد والد"
          name="parent"
          tooltip="در صورت نداشتن واحد والد، این گزینه را خالی بگذارید."
        >
          <Select
            allowClear
            showSearch
            optionFilterProp="label"
            placeholder="واحد والد را انتخاب کنید"
            options={unitParentOptions}
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
            placeholder="توضیحات مربوط به واحد..."
            maxLength={1000}
            showCount
          />
        </Form.Item>
      </Space>
    </Form>
  )
}