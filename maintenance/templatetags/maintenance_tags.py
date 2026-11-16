from django import template

register = template.Library()


@register.filter
def status_color(status):
    colors = {
        'registered': 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
        'assigned': 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300',
        'in_progress': 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
        'resolved': 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
        'closed': 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
        'reopened': 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300',
    }
    return colors.get(status, 'bg-gray-100 text-gray-600')


@register.filter
def urgency_color(urgency):
    colors = {
        'low': 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
        'medium': 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300',
        'high': 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
        'critical': 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
    }
    return colors.get(urgency, 'bg-gray-100 text-gray-600')


@register.filter
def urgency_dot(urgency):
    colors = {
        'low': 'bg-blue-500',
        'medium': 'bg-yellow-500',
        'high': 'bg-orange-500',
        'critical': 'bg-red-500 animate-pulse',
    }
    return colors.get(urgency, 'bg-gray-400')


@register.filter
def category_icon(category):
    icons = {
        'electrical': '⚡',
        'plumbing': '🔧',
        'furniture': '🪑',
        'wifi': '📶',
        'appliances': '🔌',
        'civil': '🏗️',
    }
    return icons.get(category, '📋')


@register.filter
def star_range(value):
    try:
        return range(int(value))
    except (TypeError, ValueError):
        return range(0)


@register.filter
def empty_star_range(value):
    try:
        return range(5 - int(value))
    except (TypeError, ValueError):
        return range(5)
