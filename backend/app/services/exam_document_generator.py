"""
考试文档PDF生成服务

提供座位表、准考证、监考手册等PDF文档生成功能
"""

import io
import logging
from typing import List, Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.exam_room import ExamRoom, ExamRoomStudent, ExamProctor
from app.models.evaluation import Exam
from app.models.user import User

logger = logging.getLogger(__name__)


class ExamDocumentGenerator:
    """考试文档生成器"""

    def __init__(self):
        """初始化PDF生成器"""
        self._register_fonts()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _register_fonts(self):
        """注册中文字体"""
        try:
            # 尝试注册系统中文字体
            # macOS
            font_paths = [
                '/System/Library/Fonts/PingFang.ttc',  # 苹方
                '/System/Library/Fonts/STHeiti Light.ttc',  # 黑体
                '/System/Library/Fonts/STSong.ttc',  # 宋体
            ]

            for font_path in font_paths:
                try:
                    # 注册简体中文
                    pdfmetrics.registerFont(TTFont('Chinese', font_path, subfontIndex=1))
                    logger.info(f"Successfully registered font: {font_path}")
                    break
                except:
                    continue
            else:
                logger.warning("No Chinese font found, using default font")
        except Exception as e:
            logger.error(f"Failed to register fonts: {str(e)}")

    def _setup_custom_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            parent=self.styles['Heading1'],
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
            fontSize=18,
            alignment=1,  # 居中
            spaceAfter=12,
        ))

        # 副标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseSubtitle',
            parent=self.styles['Heading2'],
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
            fontSize=14,
            alignment=1,
            spaceAfter=12,
        ))

        # 正文样式
        self.styles.add(ParagraphStyle(
            name='ChineseNormal',
            parent=self.styles['Normal'],
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
            fontSize=10,
            leading=14,
        ))

        # 小标题样式
        self.styles.add(ParagraphStyle(
            name='ChineseSmallTitle',
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
            fontSize=12,
            bold=True,
            spaceAfter=6,
        ))

    async def generate_seating_chart(
        self,
        exam_room: ExamRoom,
        exam: Exam,
        db: AsyncSession
    ) -> bytes:
        """生成座位表PDF

        Args:
            exam_room: 考场信息
            exam: 考试信息
            db: 数据库会话

        Returns:
            PDF文件字节流
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )

        story = []

        # 标题
        story.append(Paragraph(
            f"{exam.name} - {exam_room.name} 座位表",
            self.styles['ChineseTitle']
        ))

        # 考试信息
        exam_info = f"""
        考试日期：{exam.exam_date.strftime('%Y年%m月%d日')}<br/>
        考场容量：{exam_room.seat_count}/{exam_room.capacity}人<br/>
        考号范围：{exam_room.exam_number_start} - {exam_room.exam_number_end}<br/>
        """
        story.append(Paragraph(exam_info, self.styles['ChineseNormal']))
        story.append(Spacer(1, 0.5*cm))

        # 座位表
        # 获取学生信息
        result = await db.execute(
            select(ExamRoomStudent)
            .where(ExamRoomStudent.room_id == exam_room.id)
            .order_by(ExamRoomStudent.seat_number)
        )
        students = result.scalars().all()

        # 计算列数（6列：座位号、考号、姓名、学号、班级、签名）
        data = [['座位号', '考号', '姓名', '学号', '班级', '签名']]

        for student in students:
            row = [
                str(student.seat_number),
                student.exam_number,
                student.student_name or '',
                student.student_id_number or '',
                f"班级{student.classroom_id}" if student.classroom_id else '',
                ''  # 签名栏
            ]
            data.append(row)

        # 创建表格
        table = Table(data, colWidths=[2*cm, 3*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Chinese-Bold' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        story.append(table)

        # 页脚
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"打印时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            self.styles['ChineseNormal']
        ))

        # 生成PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"Generated seating chart for {exam_room.name}")
        return pdf_bytes

    async def generate_exam_tickets(
        self,
        exam_room: ExamRoom,
        exam: Exam,
        db: AsyncSession
    ) -> bytes:
        """生成准考证PDF（所有学生一页一个）

        Args:
            exam_room: 考场信息
            exam: 考试信息
            db: 数据库会话

        Returns:
            PDF文件字节流
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # 获取学生信息
        result = await db.execute(
            select(ExamRoomStudent)
            .where(ExamRoomStudent.room_id == exam_room.id)
            .order_by(ExamRoomStudent.seat_number)
        )
        students = result.scalars().all()

        # 为每个学生生成准考证
        for student in students:
            story.append(Spacer(1, 1*cm))

            # 标题
            story.append(Paragraph(
                f"{exam.name} 准考证",
                self.styles['ChineseTitle']
            ))

            # 学生信息表格
            data = [
                ['姓　　名：', student.student_name or ''],
                ['学　　号：', student.student_id_number or ''],
                ['考　　号：', student.exam_number],
                ['考　　场：', exam_room.name],
                ['座　　号：', str(student.seat_number)],
                ['考试日期：', exam.exam_date.strftime('%Y年%m月%d日')],
            ]

            table = Table(data, colWidths=[5*cm, 8*cm])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            story.append(table)
            story.append(Spacer(1, 1*cm))

            # 注意事项
            notice = """
            <b>注意事项：</b><br/>
            1. 请提前15分钟到达考场<br/>
            2. 携带本人身份证或学生证<br/>
            3. 对号入座，将证件放在座位左上角<br/>
            4. 考试期间不得擅自离开考场<br/>
            5. 严格遵守考场纪律
            """
            story.append(Paragraph(notice, self.styles['ChineseNormal']))

            # 分页（除了最后一个）
            if student != students[-1]:
                story.append(PageBreak())

        # 生成PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"Generated exam tickets for {exam_room.name} ({len(students)} students)")
        return pdf_bytes

    async def generate_proctor_handbook(
        self,
        exam_room: ExamRoom,
        exam: Exam,
        db: AsyncSession
    ) -> bytes:
        """生成监考手册PDF

        Args:
            exam_room: 考场信息
            exam: 考试信息
            db: 数据库会话

        Returns:
            PDF文件字节流
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # 标题
        story.append(Paragraph(
            f"{exam.name} 监考手册",
            self.styles['ChineseTitle']
        ))
        story.append(Spacer(1, 0.5*cm))

        # 考场基本信息
        room_info = f"""
        <b>考场信息</b><br/>
        考场名称：{exam_room.name}<br/>
        考场位置：{exam_room.name.replace('第', '教学楼') if '第' in exam_room.name else '待定'}<br/>
        考试时间：{exam.exam_date.strftime('%Y年%m月%d日')}<br/>
        考场容量：{exam_room.seat_count}/{exam_room.capacity}人<br/>
        """
        story.append(Paragraph(room_info, self.styles['ChineseNormal']))
        story.append(Spacer(1, 0.5*cm))

        # 监考教师信息
        result = await db.execute(
            select(ExamProctor)
            .where(ExamProctor.room_id == exam_room.id)
            .order_by(ExamProctor.proctor_type)
        )
        proctors = result.scalars().all()

        proctor_info = "<b>监考教师：</b><br/>"
        for proctor in proctors:
            role = "主监考" if proctor.proctor_type == "primary" else "副监考"
            # TODO: 获取教师真实姓名
            proctor_info += f"{role}：教师ID-{proctor.user_id}<br/>"

        story.append(Paragraph(proctor_info, self.styles['ChineseNormal']))
        story.append(Spacer(1, 0.5*cm))

        # 学生名单
        story.append(Paragraph("<b>学生名单：</b>", self.styles['ChineseSmallTitle']))

        result = await db.execute(
            select(ExamRoomStudent)
            .where(ExamRoomStudent.room_id == exam_room.id)
            .order_by(ExamRoomStudent.seat_number)
        )
        students = result.scalars().all()

        data = [['座位', '考号', '姓名', '班级', '签到']]
        for student in students:
            row = [
                str(student.seat_number),
                student.exam_number,
                student.student_name or '',
                f"班级{student.classroom_id}" if student.classroom_id else '',
            ]
            data.append(row)

        table = Table(data, colWidths=[2*cm, 4*cm, 4*cm, 4*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Chinese-Bold' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        story.append(table)
        story.append(PageBreak())

        # 监考职责
        duties = """
        <b>监考职责：</b><br/>
        <ol>
        <li>提前30分钟到达考场，检查考场布置</li>
        <li>核对学生证件，指导学生对号入座</li>
        <li>宣读考场纪律，强调考试规则</li>
        <li>分发试卷，核对试卷数量</li>
        <li>维护考场秩序，处理突发事件</li>
        <li>防止作弊行为，记录违纪情况</li>
        <li>考试结束后收集、整理试卷</li>
        <li>填写考场记录单</li>
        </ol>
        """
        story.append(Paragraph(duties, self.styles['ChineseNormal']))
        story.append(Spacer(1, 0.5*cm))

        # 注意事项
        notices = """
        <b>注意事项：</b><br/>
        <ol>
        <li>监考教师应佩戴监考证件</li>
        <li>不得携带手机等通讯工具进入考场</li>
        <li>不得擅自离开考场或做与监考无关的事情</li>
        <li>发现作弊行为应立即制止并记录</li>
        <li>考试结束前15分钟提醒考生</li>
        <li>确认所有试卷回收无误后方可让考生离开</li>
        </ol>
        """
        story.append(Paragraph(notices, self.styles['ChineseNormal']))

        # 签名栏
        story.append(Spacer(1, 2*cm))
        signature = f"""
        <br/><br/>
        主监考签名：__________________ 日期：{datetime.now().strftime('%Y年%m月%d日')}<br/><br/>
        副监考签名：__________________ 日期：{datetime.now().strftime('%Y年%m月%d日')}<br/>
        """
        story.append(Paragraph(signature, self.styles['ChineseNormal']))

        # 生成PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"Generated proctor handbook for {exam_room.name}")
        return pdf_bytes
